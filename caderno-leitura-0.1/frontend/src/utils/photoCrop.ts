/**
 * F0.11.10 (spec 112): geometria do recorte e do giro da foto na digitalização (funções puras).
 *
 * O recorte é guardado em frações (0–1) da imagem **já girada**. O giro é em passos de 90° no sentido horário
 * (0, 90, 180, 270). O desenho em `canvas` usa `drawTransform` e `sourceOffset`, também puros.
 */

export interface Crop {
  x: number
  y: number
  w: number
  h: number
}

export type Rotation = 0 | 90 | 180 | 270
export type CropHandle = 'nw' | 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'move'

export const CROP_MARGIN = 0.04
export const CROP_MIN = 0.1
export const MAX_OUTPUT_PIXELS = 40_000_000
export const MIN_CROP_SIDE_PX = 300

const round = (value: number) => Math.round(value * 1e6) / 1e6
const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

export function initialCrop(margin = CROP_MARGIN): Crop {
  return { x: margin, y: margin, w: round(1 - 2 * margin), h: round(1 - 2 * margin) }
}

/** Mantém o recorte dentro da imagem e com o tamanho mínimo. */
export function clampCrop(crop: Crop): Crop {
  const w = clamp(crop.w, CROP_MIN, 1)
  const h = clamp(crop.h, CROP_MIN, 1)
  return { x: round(clamp(crop.x, 0, 1 - w)), y: round(clamp(crop.y, 0, 1 - h)), w: round(w), h: round(h) }
}

export function moveCrop(crop: Crop, dx: number, dy: number): Crop {
  return clampCrop({ ...crop, x: crop.x + dx, y: crop.y + dy })
}

/** Arrasta uma alça (canto ou borda) em frações; as bordas opostas ficam paradas. */
export function moveHandle(crop: Crop, handle: CropHandle, dx: number, dy: number): Crop {
  if (handle === 'move') return moveCrop(crop, dx, dy)
  let left = crop.x
  let top = crop.y
  let right = crop.x + crop.w
  let bottom = crop.y + crop.h
  if (handle.includes('w')) left = clamp(left + dx, 0, right - CROP_MIN)
  if (handle.includes('e')) right = clamp(right + dx, left + CROP_MIN, 1)
  if (handle.includes('n')) top = clamp(top + dy, 0, bottom - CROP_MIN)
  if (handle.includes('s')) bottom = clamp(bottom + dy, top + CROP_MIN, 1)
  return { x: round(left), y: round(top), w: round(right - left), h: round(bottom - top) }
}

/** Gira o recorte junto com a imagem, para continuar sobre o mesmo trecho da página. */
export function rotateCrop(crop: Crop, direction: 'left' | 'right'): Crop {
  if (direction === 'right') {
    // (u, v) → (1 − v, u)
    return { x: round(1 - (crop.y + crop.h)), y: crop.x, w: crop.h, h: crop.w }
  }
  // (u, v) → (v, 1 − u)
  return { x: crop.y, y: round(1 - (crop.x + crop.w)), w: crop.h, h: crop.w }
}

export function rotate(rotation: Rotation, direction: 'left' | 'right'): Rotation {
  return (((rotation + (direction === 'right' ? 90 : 270)) % 360) as Rotation)
}

/** Largura e altura da imagem depois do giro. */
export function rotatedSize(width: number, height: number, rotation: Rotation): { width: number; height: number } {
  return rotation % 180 === 0 ? { width, height } : { width: height, height: width }
}

/** Tamanho do recorte em pixels e a escala para caber no limite do servidor. */
export function outputSize(
  naturalWidth: number,
  naturalHeight: number,
  crop: Crop,
  rotation: Rotation,
  maxPixels = MAX_OUTPUT_PIXELS,
): { width: number; height: number; scale: number } {
  const rotated = rotatedSize(naturalWidth, naturalHeight, rotation)
  const cropWidth = Math.max(1, crop.w * rotated.width)
  const cropHeight = Math.max(1, crop.h * rotated.height)
  const scale = Math.min(1, Math.sqrt(maxPixels / (cropWidth * cropHeight)))
  return {
    width: Math.max(1, Math.round(cropWidth * scale)),
    height: Math.max(1, Math.round(cropHeight * scale)),
    scale: round(scale),
  }
}

/** Transformação que desenha a imagem original no espaço da imagem girada (para `ctx.translate` + `ctx.rotate`). */
export function drawTransform(rotation: Rotation, rotatedWidth: number, rotatedHeight: number) {
  switch (rotation) {
    case 90: return { tx: rotatedWidth, ty: 0, angle: Math.PI / 2 }
    case 180: return { tx: rotatedWidth, ty: rotatedHeight, angle: Math.PI }
    case 270: return { tx: 0, ty: rotatedHeight, angle: -Math.PI / 2 }
    default: return { tx: 0, ty: 0, angle: 0 }
  }
}

/** Canto superior esquerdo do recorte em pixels da imagem girada. */
export function sourceOffset(naturalWidth: number, naturalHeight: number, crop: Crop, rotation: Rotation) {
  const rotated = rotatedSize(naturalWidth, naturalHeight, rotation)
  return { x: crop.x * rotated.width, y: crop.y * rotated.height }
}

export function isWholeImage(crop: Crop, rotation: Rotation): boolean {
  return rotation === 0 && crop.x <= 0.001 && crop.y <= 0.001 && crop.w >= 0.999 && crop.h >= 0.999
}

export function describeCrop(crop: Crop): string {
  const pct = (value: number) => `${Math.round(value * 100)}%`
  return `Recorte: ${pct(crop.x)} a ${pct(crop.x + crop.w)} na largura, ${pct(crop.y)} a ${pct(crop.y + crop.h)} na altura.`
}

/** Passo do teclado: 1% (5% com Shift). */
export function keyboardDelta(key: string, shift: boolean): { dx: number; dy: number } | null {
  const step = shift ? 0.05 : 0.01
  switch (key) {
    case 'ArrowLeft': return { dx: -step, dy: 0 }
    case 'ArrowRight': return { dx: step, dy: 0 }
    case 'ArrowUp': return { dx: 0, dy: -step }
    case 'ArrowDown': return { dx: 0, dy: step }
    default: return null
  }
}
