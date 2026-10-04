import { computed, type Ref } from 'vue'
import type {
  StudySummary,
  StudyRelationItem,
  StudyRelationType,
  MapNodeItem,
  MapConnectionEdge,
} from '../types.ts'
import { RELATION_TYPE_LABELS } from './useStudyRelations.ts'

export interface MapLayoutOptions {
  width: number
  height: number
  cx: number
  cy: number
  primaryRadius: number
  secondaryRadius: number
  minAngularSeparation: number
}

export const DEFAULT_MAP_LAYOUT_OPTIONS: MapLayoutOptions = {
  width: 700,
  height: 500,
  cx: 350,
  cy: 250,
  primaryRadius: 160,
  secondaryRadius: 260,
  minAngularSeparation: Math.PI / 8, // ~22.5 graus
}

/**
 * Calcula a projeção radial concêntrica dos estudos com destaque do Estudo Núcleo.
 * Função pura e determinística ideal para memoização e testes sem dependências de DOM.
 */
export function computeRadialLayout(
  studies: StudySummary[],
  relations: StudyRelationItem[],
  activeStudyId: number | null = null,
  customOptions?: Partial<MapLayoutOptions>
): {
  coreNode: MapNodeItem | null
  nodes: MapNodeItem[]
  edges: MapConnectionEdge[]
} {
  if (!studies || studies.length === 0) {
    return { coreNode: null, nodes: [], edges: [] }
  }

  const opts: MapLayoutOptions = { ...DEFAULT_MAP_LAYOUT_OPTIONS, ...customOptions }

  // 1. Contagem de grau de cada estudo (quantas relações possui)
  const degrees = new Map<number, number>()
  for (const s of studies) {
    degrees.set(s.id, 0)
  }
  for (const r of relations) {
    if (degrees.has(r.source_study_id)) {
      degrees.set(r.source_study_id, (degrees.get(r.source_study_id) || 0) + 1)
    }
    if (degrees.has(r.target_study_id)) {
      degrees.set(r.target_study_id, (degrees.get(r.target_study_id) || 0) + 1)
    }
  }

  // 2. Determinação do Estudo Núcleo (Core Node)
  let coreStudy: StudySummary = studies[0]
  if (activeStudyId !== null) {
    const found = studies.find((s) => s.id === activeStudyId)
    if (found) {
      coreStudy = found
    }
  } else {
    // Se não há estudo ativo explícito, seleciona o estudo com mais conexões
    let maxDegree = -1
    for (const s of studies) {
      const deg = degrees.get(s.id) || 0
      if (deg > maxDegree) {
        maxDegree = deg
        coreStudy = s
      }
    }
  }

  // 3. Classificação dos nós nos anéis (Primário se conectado diretamente ao núcleo, Secundário caso contrário)
  const directConnectedIds = new Set<number>()
  for (const r of relations) {
    if (r.source_study_id === coreStudy.id) {
      directConnectedIds.add(r.target_study_id)
    } else if (r.target_study_id === coreStudy.id) {
      directConnectedIds.add(r.source_study_id)
    }
  }

  const primaryStudies: StudySummary[] = []
  const secondaryStudies: StudySummary[] = []

  for (const s of studies) {
    if (s.id === coreStudy.id) continue
    if (directConnectedIds.has(s.id)) {
      primaryStudies.push(s)
    } else {
      secondaryStudies.push(s)
    }
  }

  // 4. Criação do nó núcleo ao centro
  const coreNode: MapNodeItem = {
    study: coreStudy,
    x: opts.cx,
    y: opts.cy,
    angle: 0,
    ring: 'core',
    isCore: true,
    degree: degrees.get(coreStudy.id) || 0,
  }

  const allNodes: MapNodeItem[] = [coreNode]

  // 5. Distribuição angular e repulsão suave no anel primário (R1)
  if (primaryStudies.length > 0) {
    const pCount = primaryStudies.length
    const angles = primaryStudies.map((_, i) => (2 * Math.PI * i) / pCount - Math.PI / 2)

    // Passe de relaxamento repulsivo simples para nós vizinhos
    applyAngularRepulsion(angles, opts.minAngularSeparation)

    primaryStudies.forEach((s, i) => {
      const ang = angles[i]
      allNodes.push({
        study: s,
        x: Math.round(opts.cx + opts.primaryRadius * Math.cos(ang)),
        y: Math.round(opts.cy + opts.primaryRadius * Math.sin(ang)),
        angle: ang,
        ring: 'primary',
        isCore: false,
        degree: degrees.get(s.id) || 0,
      })
    })
  }

  // 6. Distribuição angular e repulsão suave no anel secundário (R2)
  if (secondaryStudies.length > 0) {
    const sCount = secondaryStudies.length
    // Offset de meio passo para intercalar visualmente com os nós do anel primário
    const offset = Math.PI / (sCount || 1)
    const angles = secondaryStudies.map(
      (_, i) => (2 * Math.PI * i) / sCount - Math.PI / 2 + offset
    )

    applyAngularRepulsion(angles, opts.minAngularSeparation * 0.75)

    secondaryStudies.forEach((s, i) => {
      const ang = angles[i]
      allNodes.push({
        study: s,
        x: Math.round(opts.cx + opts.secondaryRadius * Math.cos(ang)),
        y: Math.round(opts.cy + opts.secondaryRadius * Math.sin(ang)),
        angle: ang,
        ring: 'secondary',
        isCore: false,
        degree: degrees.get(s.id) || 0,
      })
    })
  }

  // Mapa plano id -> MapNodeItem
  const nodeMap = new Map<number, MapNodeItem>()
  for (const n of allNodes) {
    nodeMap.set(n.study.id, n)
  }

  // 7. Cálculo das arestas direcionadas curvas em SVG
  const edges: MapConnectionEdge[] = []
  for (const r of relations) {
    const src = nodeMap.get(r.source_study_id)
    const tgt = nodeMap.get(r.target_study_id)
    if (src && tgt && src.study.id !== tgt.study.id) {
      const dx = tgt.x - src.x
      const dy = tgt.y - src.y
      const mx = (src.x + tgt.x) / 2
      const my = (src.y + tgt.y) / 2

      // Ponto de controle perpendicular proporcional à distância
      const dist = Math.hypot(dx, dy)
      const curvature = dist > 40 ? 0.18 : 0.05
      const cx = Math.round(mx - dy * curvature)
      const cy = Math.round(my + dx * curvature)

      // Ponto médio exato da curva quadrática B(0.5) = 0.25*src + 0.5*ctrl + 0.25*tgt
      const badgeX = Math.round(0.25 * src.x + 0.5 * cx + 0.25 * tgt.x)
      const badgeY = Math.round(0.25 * src.y + 0.5 * cy + 0.25 * tgt.y)

      const typeMeta = RELATION_TYPE_LABELS[r.relation_type as StudyRelationType]
      const label = typeMeta ? typeMeta.outbound : r.relation_type

      edges.push({
        id: r.id,
        sourceStudyId: r.source_study_id,
        targetStudyId: r.target_study_id,
        relationType: r.relation_type as StudyRelationType,
        description: r.description || null,
        path: `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`,
        label,
        badgeX,
        badgeY,
        isContradiction: r.relation_type === 'contradiz',
      })
    }
  }

  return { coreNode, nodes: allNodes, edges }
}

/**
 * Relaxamento angular suave que afasta ângulos adjacentes que estejam mais próximos
 * que a separação mínima permitida, preservando a simetria global da órbita.
 */
function applyAngularRepulsion(angles: number[], minSeparation: number, iterations = 3) {
  if (angles.length <= 1) return

  for (let it = 0; it < iterations; it++) {
    for (let i = 0; i < angles.length; i++) {
      for (let j = i + 1; j < angles.length; j++) {
        let diff = angles[j] - angles[i]
        // Normaliza diferença para [-PI, PI]
        while (diff > Math.PI) diff -= 2 * Math.PI
        while (diff < -Math.PI) diff += 2 * Math.PI

        const absDiff = Math.abs(diff)
        if (absDiff < minSeparation && absDiff > 0.0001) {
          const shift = ((minSeparation - absDiff) / 2) * Math.sign(diff)
          angles[i] -= shift * 0.4
          angles[j] += shift * 0.4
        }
      }
    }
  }
}

/**
 * Composable reativo que encapsula o layout do mapa conceitual.
 */
export function useMapLayout(
  studiesRef: Ref<StudySummary[]>,
  relationsRef: Ref<StudyRelationItem[]>,
  activeStudyIdRef: Ref<number | null | undefined>,
  options?: Partial<MapLayoutOptions>
) {
  const layout = computed(() => {
    return computeRadialLayout(
      studiesRef.value,
      relationsRef.value,
      activeStudyIdRef.value ?? null,
      options
    )
  })

  const coreNode = computed(() => layout.value.coreNode)
  const nodes = computed(() => layout.value.nodes)
  const edges = computed(() => layout.value.edges)

  const nodesById = computed(() => {
    const map = new Map<number, MapNodeItem>()
    for (const n of nodes.value) {
      map.set(n.study.id, n)
    }
    return map
  })

  return {
    coreNode,
    nodes,
    edges,
    nodesById,
    dimensions: DEFAULT_MAP_LAYOUT_OPTIONS,
  }
}
