export interface UserRead {
  id: string
  username: string
  display_name: string
  email?: string | null
  role?: string
  status: string
  created_at: string
  has_password?: boolean
  has_google?: boolean
}

export interface AuthConfigResponse {
  allow_registration: boolean
  owner_setup_required: boolean
  google_auth_enabled?: boolean
  google_client_id?: string | null
}

export interface ExternalIdentityRead {
  id: string
  provider: string
  email_at_link?: string | null
  created_at: string
}

export interface GoogleAuthRequest {
  credential: string
}

export interface AuthSuccessResponse {
  user: UserRead
  session_id: string
}

export interface SessionItem {
  id: string
  device_name: string
  ip_address: string
  created_at: string
  last_activity: string
  expires_at: string
  is_current: boolean
}

export interface AccountDeactivatedResponse {
  code: string
  message: string
}

export interface RateLimitResponse {
  detail: string
  retry_after?: number
}

export interface AuditLogItem {
  id: string
  created_at: string
  event_type: string
  user_id: string | null
  actor_username: string | null
  ip_address: string | null
  user_agent: string | null
  details: Record<string, any> | null
}

export interface AuditLogListResponse {
  items: AuditLogItem[]
  total: number
  limit: number
  offset: number
}

export interface DeactivateAccountRequest {
  password?: string
}

export interface ReactivateAccountRequest {
  username_or_email: string
  password?: string
  google_credential?: string
}

export interface DeleteAccountRequest {
  password?: string
  confirmation_text: string
}


export interface Category {
  id: string
  name: string
  parent_id: string | null
  path: string
  user_id?: string | null
  is_canonical?: boolean
  books_count?: number
  created_at?: string | null
}

export interface CategorySuggestion {
  input_term: string
  suggested_canonical: string
  is_exact_match: boolean
  matching_candidates: Category[]
}

export interface CategoryStats {
  total_categories: number
  canonical_categories: number
  unused_categories: number
  total_book_associations: number
}

export interface Book {
  id: number
  user_id?: string
  title: string
  author: string | null
  subtitle?: string | null
  year?: number | null
  cover_image?: string | null
  created_at?: string | null
  updated_at?: string | null
  deleted_at?: string | null
  categories?: Category[]
  version?: number
  visibility?: 'private' | 'friends' | 'public'
  can_edit?: boolean
  owner?: { id: string; username: string; display_name: string; avatar_url?: string | null } | null
}

export type LibraryViewMode = 'grid' | 'list'

export type BookSortOption =
  | 'title-asc'
  | 'title-desc'
  | 'author-asc'
  | 'recent-created'
  | 'recent-updated'
  | 'oldest-created'
  | 'year-desc'

export interface LibraryFilterState {
  searchQuery: string
  selectedCategory: string | null
  viewMode: LibraryViewMode
  sortBy: BookSortOption
}

export interface BookCreatePayload {
  title: string
  author?: string | null
  subtitle?: string | null
  year?: number | null
  category_ids?: string[]
}

export interface BookPatch {
  title?: string
  author?: string | null
  subtitle?: string | null
  year?: number | null
  cover_image?: string | null
  expected_updated_at?: string | null
  expected_version?: number | null
  category_ids?: string[]
}

export interface CoverResponse {
  book_id: number
  cover_image: string | null
  cover_url: string | null
  message: string
}

export interface Chapter {
  id: number
  book_id: number
  name: string
  position: number
  created_at?: string | null
  updated_at?: string | null
}

export interface ChapterPatch {
  name?: string
  expected_updated_at?: string | null
}

export interface StudySummary {
  id: number
  chapter_id: number
  title: string
  location: string
  parent_study_id?: number | null
  position?: number
  reading_status?: ReadingStatus
  created_at: string
  updated_at: string
  deleted_at?: string | null
  version?: number
  book_id?: number | null
  visibility?: 'inherit' | 'private' | 'friends' | 'custom' | 'public'
  effective_visibility?: 'inherit' | 'private' | 'friends' | 'custom' | 'public'
  can_edit?: boolean
  owner?: { id: string; username: string; display_name: string; avatar_url?: string | null } | null
  summary_preview?: string
  highlights_count?: number
  relations_count?: number
  has_summary?: boolean
  has_explanation?: boolean
  has_concepts?: boolean
  has_references?: boolean
}

export type SortColumn = 'natural' | 'title' | 'status' | 'date'
export type SortDirection = 'asc' | 'desc' | 'default'

export interface StudyListFilterState {
  searchQuery: string
  statusFilter: ReadingStatus | 'all'
  sortColumn: SortColumn
  sortDirection: SortDirection
}

export interface BranchProgressDetails {
  rascunho: number
  em_andamento: number
  revisado: number
  concluido: number
}

export interface BranchProgress {
  total: number
  completed: number
  percent: number
  label: string
  details: BranchProgressDetails
}

export interface StudyTreeNode extends StudySummary {
  parent_study_id: number | null
  position: number
  depth: number
  children: StudyTreeNode[]
  progress?: BranchProgress | null
}

export interface StudyMovePayload {
  parent_study_id: number | null
  target_position: number
  expected_updated_at?: string | null
}

export interface AnalysisSections {
  summary: string
  explanation: string
  concepts: string
  references: string
}

export interface Study extends StudySummary, AnalysisSections {
  source_response: string
  notes: string
}

export type StudyPatch = Partial<AnalysisSections & Pick<Study, 'title' | 'location' | 'notes'>> & {
  expected_updated_at?: string | null
  expected_version?: number | null
}

export interface StudyContext {
  book: Book
  chapter: Chapter
  study: Study
}

export interface StudyCreate extends AnalysisSections {
  chapter_id: number
  title: string | null
  location: string
  source_response: string
  notes: string
}

export interface ImportWarning {
  code: string
  message: string
  section: string | null
  line: number | null
}

export interface ImportPreview extends AnalysisSections {
  source_response: string
  unassigned_text: string
  warnings: ImportWarning[]
}

export const SECTION_LABELS = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
] as const

export type EditorSectionTabKey = 'summary' | 'explanation' | 'concepts' | 'references' | 'notes'
export type EditorViewMode = 'focused' | 'all'

export interface EditorSectionTab {
  key: EditorSectionTabKey
  label: string
  hasContent: boolean
  isPreviewing?: boolean
}

export const EDITOR_SECTION_TABS = [
  { key: 'summary', label: 'Resumo' },
  { key: 'explanation', label: 'Explicação' },
  { key: 'concepts', label: 'Conceitos' },
  { key: 'references', label: 'Referências' },
  { key: 'notes', label: 'Notas' },
] as const

export interface StudyEditorDraftPayload {
  studyId: number
  title: string
  location: string
  sections: AnalysisSections
  notes: string
  savedAt: number
}

export type StudyEditorDraft = StudyEditorDraftPayload

export function positiveId(value: unknown): number | null {
  if (typeof value !== 'string' || !/^\d+$/.test(value)) return null
  const id = Number(value)
  return Number.isSafeInteger(id) && id > 0 ? id : null
}

export interface TrashBookItem {
  id: number
  title: string
  author: string | null
  deleted_at: string
  days_until_purge: number
  chapters_count: number
  studies_count: number
}

export interface TrashStudyItem {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_name: string
  deleted_at: string
  days_until_purge: number
}

export interface TrashSummary {
  books: TrashBookItem[]
  studies: TrashStudyItem[]
  total_items: number
}

export interface TrashActionResponse {
  id: number
  title: string
  deleted_at?: string | null
  book_restored?: boolean
}

export interface TrashEmptyResponse {
  purged_books: number
  purged_studies: number
  message: string
}

export interface RecentStudyActivityItem {
  study_id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_title: string | null
  reading_status: ReadingStatus | string
  updated_at: string
}

export interface UnlinkedStudyItem {
  study_id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_title: string | null
  reading_status: ReadingStatus | string
  created_at: string
}

export interface RecentRelationItem {
  relation_id: number
  relation_type: StudyRelationType | string
  description: string | null
  source_study_id: number
  source_study_title: string
  source_book_id: number
  source_book_title: string
  target_study_id: number
  target_study_title: string
  target_book_id: number
  target_book_title: string
  created_at: string
}

export interface DashboardSummary {
  total_books: number
  total_studies: number
  total_reading_days: number
  current_streak: number
  avg_studies_per_book: number
  total_relations: number
  total_categories: number
  unlinked_studies_count: number
}

export interface HeatmapPoint {
  date: string
  count: number
  level: number
}

export type TimelineAction = 'book_created' | 'study_created' | 'study_updated'
export type TimelineEntityType = 'book' | 'study'

export interface TimelineItem {
  id: string
  entity_type: TimelineEntityType
  action: TimelineAction
  timestamp: string
  title: string
  book_id: number
  book_title: string
  chapter_id?: number | null
  chapter_title?: string | null
  study_id?: number | null
}

export interface DashboardResponse {
  summary: DashboardSummary
  heatmap: HeatmapPoint[]
  timeline: TimelineItem[]
  recent_studies: RecentStudyActivityItem[]
  unlinked_studies: UnlinkedStudyItem[]
  latest_relations: RecentRelationItem[]
}

export type HomeViewPreference = 'dashboard' | 'books'

export interface DashboardBlockVisibility {
  resumeStudies: boolean
  unlinkedStudies: boolean
  recentRelations: boolean
  timelineHeatmap: boolean
}

export interface DashboardParams {
  tz_offset?: number
  days?: number
  date?: string | null
  limit?: number
}

export type SettingsTabId = 'perfil' | 'aparencia' | 'leitura' | 'sistema' | 'conta'

export interface SettingsTab {
  id: SettingsTabId
  label: string
  description: string
}

export interface StorageDiagnostic {
  isAvailable: boolean
  keyCount: number
  totalBytes: number
  formattedSize: string
  cadernoKeysCount: number
}

export interface HealthCheckResult {
  status: 'loading' | 'ok' | 'error'
  version: string | null
  latencyMs: number | null
  message: string
}

export interface ConfirmResetModalState {
  isOpen: boolean
  isBusy: boolean
  feedback: string | null
}

export type ExportFormat = 'markdown' | 'text'
export type ExportType = 'full' | 'digest'

export interface ExportConfig {
  format: ExportFormat
  exportType: ExportType
  includeNotes: boolean
  includeSections: boolean
  includeSource: boolean
  includeMetadata: boolean
  includeHighlights: boolean
  exerciseMode: boolean
}

export interface ExportModalProps {
  open: boolean
  title: string
  scope: 'book' | 'study'
  bookId: number
  studyId?: number | null
}

export interface BackupCounts {
  books: number
  chapters: number
  studies: number
  covers: number
}

export interface BackupManifest {
  app_version: string
  schema_version: string | null
  created_at: string
  generator: string
  counts: BackupCounts
  files: Record<string, string>
}

export interface RestoreResult {
  success: boolean
  message: string
  backup_created_at?: string | null
  pre_restore_snapshot: string
  schema_revision?: string | null
  counts: Record<string, number>
  covers_restored: number
}

export interface ConcurrencyConflictState {
  hasConflict: boolean
  message: string
  clientUpdatedAt: string | null
  serverUpdatedAt?: string | null
}

export type ConcurrencyResolutionAction = 'overwrite' | 'reload'

// --- Sistema Visual Profissional (F09) ---

export type IconName =
  | 'book-open'
  | 'book'
  | 'layout-dashboard'
  | 'plus'
  | 'sliders'
  | 'trash'
  | 'trash-restore'
  | 'rotate-ccw'
  | 'copy'
  | 'heart'
  | 'pencil'
  | 'x'
  | 'search'
  | 'alert-triangle'
  | 'check-circle'
  | 'check'
  | 'flame'
  | 'folder'
  | 'calendar'
  | 'download'
  | 'upload'
  | 'external-link'
  | 'chevron-right'
  | 'chevron-down'
  | 'chevron-up'
  | 'grid'
  | 'list'
  | 'network'
  | 'canvas'
  | 'grip-vertical'
  | 'more-horizontal'
  | 'arrow-up'
  | 'arrow-down'
  | 'corner-down-right'
  | 'corner-up-left'
  | 'maximize-2'
  | 'minimize-2'
  | 'link'
  | 'arrow-right'
  | 'user'
  | 'smartphone'
  | 'monitor'
  | 'shield'
  | 'lock'
  | 'globe'
  | 'users'
  | 'camera'
  | 'image'
  | 'eye'
  | 'eye-off'
  | 'user-plus'
  | 'user-minus'
  | 'ban'
  | 'clock'
  | 'unlock'
  | 'mail'
  | 'chevron-left'
  | 'log-out'
  | 'refresh-cw'
  | 'user-check'
  | 'user-x'
  | 'bell'
  | 'bell-ring'

export interface IconProps {
  name: IconName
  size?: number | string
  strokeWidth?: number | string
  ariaLabel?: string
  class?: string
}

export interface EmptyStateProps {
  icon: IconName
  title: string
  description?: string
  headingLevel?: 'h2' | 'h3' | 'h4'
}

export interface LoadingSkeletonProps {
  shape?: 'rect' | 'circle' | 'text'
  width?: string
  height?: string
  lines?: number
  gap?: string
}

export type BadgeVariant = 'neutral' | 'accent' | 'warning' | 'danger' | 'success'

export interface StatusBadgeProps {
  variant?: BadgeVariant
  icon?: IconName
  label: string
}

// --- Painéis Redimensionáveis (F06) ---

export type PaneId = 'left' | 'right'
export type LayoutMode = 'split' | 'drawer' | 'mobile'

export interface PaneConfig {
  id: PaneId
  minWidth?: number
  maxWidth?: number
  defaultWidth?: number
  collapsible?: boolean
  defaultCollapsed?: boolean
}

export interface PaneState {
  width: number
  collapsed: boolean
  isDragging: boolean
}

export interface SplitLayoutDimensions {
  leftWidth: number
  rightWidth: number
  leftCollapsed: boolean
  rightCollapsed: boolean
  updatedAt: string
}

// --- Sistema de Visualizações (F01) ---

export type StudyViewMode = 'grid' | 'list' | 'tree' | 'map' | 'canvas'

export interface StudyViewOption {
  id: StudyViewMode
  label: string
  icon: IconName
  description: string
}

export interface ViewPreferenceState {
  bookId?: number | string | null
  mode: StudyViewMode
  updatedAt: string
}

export const STUDY_VIEW_OPTIONS: StudyViewOption[] = [
  {
    id: 'grid',
    label: 'Grade',
    icon: 'grid',
    description: 'Cartões visuais com ênfase em capas, localização e resumos'
  },
  {
    id: 'list',
    label: 'Lista',
    icon: 'list',
    description: 'Apresentação compacta em alta densidade de leitura'
  },
  {
    id: 'tree',
    label: 'Árvore',
    icon: 'folder',
    description: 'Hierarquia visual com nós expansíveis e ramos de estudo'
  },
  {
    id: 'map',
    label: 'Mapa',
    icon: 'network',
    description: 'Rede bidimensional de conceitos e conexões'
  },
  {
    id: 'canvas',
    label: 'Canvas',
    icon: 'canvas',
    description: 'Espaço 2D livre com exploração espacial flexível'
  }
]

// --- Canvas de Estudos (F03) ---

export interface StudyCanvasNode {
  id: number
  study_id: number
  book_id: number
  pos_x: number
  pos_y: number
  width: number | null
  height: number | null
  z_index: number
  color_tag: string | null
  updated_at: string
  version?: number
}

export interface CanvasViewportState {
  pan_x: number
  pan_y: number
  zoom_level: number
}

export interface CanvasPositionedCard {
  study_id: number
  x: number
  y: number
  width?: number | null
  height?: number | null
  z_index: number
  color_tag?: string | null
  is_persisted: boolean
}

export interface CanvasBoundingBox {
  min_x: number
  min_y: number
  max_x: number
  max_y: number
  width: number
  height: number
}

export interface CanvasSelectionState {
  selected_ids: Set<number>
  marquee_active: boolean
  marquee_start_x: number
  marquee_start_y: number
  marquee_current_x: number
  marquee_current_y: number
}

export interface CanvasBatchUpdateItem {
  study_id: number
  pos_x: number
  pos_y: number
  width?: number | null
  height?: number | null
  z_index?: number
  color_tag?: string | null
}

export interface CanvasBatchUpdatePayload {
  nodes: CanvasBatchUpdateItem[]
}

export interface BookCanvasResponse {
  book_id: number
  nodes: StudyCanvasNode[]
}

export type StudyRelationType =
  | 'relacionado_com'
  | 'complementa'
  | 'contradiz'
  | 'depende_de'
  | 'mesmo_tema'
  | 'desdobramento_de'

export interface ConnectedStudySummary {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number
  chapter_title: string
}

export interface StudyRelationItem {
  id: number
  source_study_id: number
  target_study_id: number
  relation_type: StudyRelationType
  description: string
  created_at: string
  connected_study: ConnectedStudySummary
}

export interface StudyRelationsResponse {
  study_id: number
  outbound: StudyRelationItem[]
  inbound: StudyRelationItem[]
}

export interface CreateStudyRelationPayload {
  target_study_id: number
  relation_type: StudyRelationType
  description?: string
}

export interface UpdateStudyRelationPayload {
  relation_type?: StudyRelationType
  description?: string
}

export interface CandidateStudyItem {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number
  chapter_title: string
}

export interface BookCanvasRelationItem {
  id: number
  source_study_id: number
  target_study_id: number
  relation_type: StudyRelationType
  description: string
}

// --- Grafo Semântico e Map View (F 0.7.7) ---

export interface MapNodeItem {
  study: StudySummary
  x: number
  y: number
  angle: number
  ring: 'core' | 'primary' | 'secondary'
  isCore: boolean
  degree: number
}

export interface MapConnectionEdge {
  id: number
  sourceStudyId: number
  targetStudyId: number
  relationType: StudyRelationType
  description: string | null
  path: string
  label: string
  badgeX: number
  badgeY: number
  isContradiction: boolean
}

export interface RelationPopoverState {
  isOpen: boolean
  sourceNode: MapNodeItem | null
  targetNode: MapNodeItem | null
  existingRelationId: number | null
  selectedType: StudyRelationType
  description: string
  isReversed: boolean
  anchorX: number
  anchorY: number
}

export interface QuickCreateState {
  isOpen: boolean
  x: number
  y: number
  sourceNodeId: number | null
  title: string
  sectionKey: 'summary' | 'concepts' | 'explanation'
  sectionContent: string
}

export interface MapViewportState {
  panX: number
  panY: number
  zoomLevel: number
}

// --- Agrupamento Visual e Status de Leitura (F05) ---

export type ReadingStatus = 'rascunho' | 'em_estudo' | 'em_andamento' | 'revisado' | 'concluido'

export type StudyGroupByCriteria = 'chapter' | 'status' | 'category' | 'date' | 'manual'

export interface StudyStatusUpdatePayload {
  reading_status: ReadingStatus
  expected_updated_at?: string | null
}

export interface StudyStatusResponse {
  id: number
  reading_status: ReadingStatus
  updated_at: string
}

export interface CanvasFrameItem {
  id: number
  book_id: number
  title: string
  color: string
  pos_x: number
  pos_y: number
  width: number
  height: number
  created_at: string
  updated_at: string
}

export interface CreateCanvasFramePayload {
  title: string
  color?: string
  pos_x: number
  pos_y: number
  width?: number
  height?: number
}

export interface UpdateCanvasFramePayload {
  title?: string
  color?: string
  pos_x?: number
  pos_y?: number
  width?: number
  height?: number
}

// --- Tipos de Mesa Espacial e Smart Snapping (F 0.7.8) ---

export type CanvasToolMode = 'select' | 'pan' | 'frame' | 'connect'

export interface SnappingTarget {
  x: number
  y: number
  width: number
  height: number
  id?: number | string
}

export interface SmartGuide {
  type: 'horizontal' | 'vertical'
  coordinate: number
  start: number
  end: number
}

export interface SnappedPosition {
  x: number
  y: number
  guides: SmartGuide[]
}

export interface CanvasQuickCreateState {
  isOpen: boolean
  worldX: number
  worldY: number
  clientX: number
  clientY: number
  connectedSourceId?: number | null
}


export interface StudyGroup<T = any> {
  id: string
  title: string
  badgeLabel?: string
  badgeClass?: string
  count: number
  isCollapsed: boolean
  studies: T[]
}

export interface SearchMatchItem {
  study_id: number
  study_title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_name: string | null
  reading_status: ReadingStatus | string
  matched_field: string
  snippet: string
  updated_at: string
}

export interface SearchResponse {
  query: string
  mode: 'and' | 'or'
  total: number
  results: SearchMatchItem[]
  suggest_or: boolean
}

export interface SearchHistoryItem {
  id: number
  query: string
  created_at: string
  updated_at: string
}

export interface SearchHistoryResponse {
  items: SearchHistoryItem[]
}

// ============================================================================
// F10 — Cinemática, Física e Aceleração Gráfica das Superclasses
// ============================================================================

export interface KinematicProfile {
  name: 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'
  friction: number
  springStiffness: number
  snapGridSize: number
  parallaxFactor: number
  revealDistance: number
  hapticStyle: 'smooth' | 'snap' | 'none' | 'subtle'
}

export interface AccelerationEngineState {
  nodeCount: number
  threshold: number
  isAccelerated: boolean
  fpsTarget: number
  reducedMotionActive: boolean
}

export interface MotionState {
  x: number
  y: number
  vx: number
  vy: number
  isDragging: boolean
  isSettling: boolean
}

// ============================================================================
// F09.5.2 — Contraste Dinâmico e Navegação Móvel
// ============================================================================

export interface ContrastCalculationOptions {
  targetRatio?: number
  lightColor?: string
  darkColor?: string
  parentBackground?: string
  highContrast?: boolean
}

export interface ContrastResult {
  textColor: string
  contrastRatio: number
  meetsAA: boolean
  meetsAAA: boolean
  luminance: number
  isDarkBackground: boolean
}

export interface DynamicThemeVariables {
  '--dynamic-fg': string
  '--dynamic-hover-bg': string
  '--dynamic-hover-fg': string
  '--dynamic-active-bg': string
  '--dynamic-active-fg': string
  '--dynamic-border': string
}

export interface MobileNavItem {
  id: string
  to?: string
  label: string
  icon: IconName
  action?: () => void
  badgeCount?: number
  isActive: boolean
}

export interface MobileMoreMenuItem {
  id: string
  to?: string
  label: string
  icon: IconName
  badgeCount?: number
  action?: () => void
  requiresAdmin?: boolean
  danger?: boolean
}

export * from './types/sync.ts'
export * from './types/preferences.ts'
export * from './types/profile.ts'
export * from './types/friendship.ts'
export * from './types/sharing.ts'

import type { HighlightColor } from './types/toolbar.ts'
export * from './types/toolbar.ts'
export type HighlightKind = 'highlight' | 'note' | 'quote' | 'hidden' | 'question'
export type StudySectionKey = 'summary' | 'explanation' | 'concepts' | 'references' | 'source_response'

export interface StudyHighlight {
  id: number
  study_id: number
  user_id: string
  section: StudySectionKey
  start_offset: number
  end_offset: number
  selected_text: string
  prefix: string
  suffix: string
  color: HighlightColor
  kind: HighlightKind
  note: string
  created_at: string
  updated_at: string
  last_reviewed_at?: string | null
  review_count?: number
  last_rating?: ReviewRating | null
}

export type ReviewRating = 'easy' | 'medium' | 'hard'

export interface ReviewBookItem {
  book_id: number
  title: string
  items_count: number
}

export interface ReviewStatsResponse {
  total_eligible: number
  total_questions: number
  total_hidden: number
  reviewed_today: number
  pending_review: number
  books: ReviewBookItem[]
}

export interface ReviewItemRead {
  id: number
  study_id: number
  study_title: string
  book_id: number
  book_title: string
  chapter_id: number
  chapter_name: string
  kind: 'question' | 'hidden'
  section: string
  question_text: string
  expected_answer: string
  context_prefix: string
  context_suffix: string
  last_reviewed_at: string | null
  review_count: number
  last_rating: ReviewRating | null
}

export interface ReviewRecordRequest {
  rating: ReviewRating
}


export interface StudyHighlightCreatePayload {
  section: StudySectionKey
  start_offset: number
  end_offset: number
  selected_text: string
  prefix?: string
  suffix?: string
  color?: HighlightColor
  kind?: HighlightKind
  note?: string
}

export interface StudyHighlightUpdatePayload {
  color?: HighlightColor
  kind?: HighlightKind
  note?: string
}

export interface TextSelectionContext {
  section: StudySectionKey
  selected_text: string
  prefix: string
  suffix: string
  start_offset: number
  end_offset: number
  boundingRect: DOMRect
}

export interface ActiveStudyNode {
  highlight_id: number
  kind: 'hidden' | 'question'
  section: StudySectionKey
  dom_element?: HTMLElement | null
  is_revealed: boolean
  prompt_text?: string
  answer_text?: string
}

export interface ActiveReadingSessionState {
  isActive: boolean
  currentSection: StudySectionKey
  nodes: ActiveStudyNode[]
  focusedIndex: number
  revealedCount: number
  totalCount: number
  completionPercentage: number
}

export type ActiveReadingSessionEvent = 'reveal-all' | 'hide-all' | 'next' | 'previous' | 'close'

export interface StudyVersionSummary {
  id: number
  study_id: number
  version_number: number
  user_id?: string | null
  author_name?: string | null
  change_summary: string
  char_count: number
  highlights_count: number
  is_current: boolean
  created_at: string
  updated_at: string
}

export interface StudyVersionDetail extends StudyVersionSummary {
  title: string
  summary: string
  explanation: string
  concepts: string
  references: string
  notes: string
  highlights: StudyHighlight[]
}

export interface DiffChunk {
  type: 'equal' | 'insert' | 'delete'
  text: string
}

export interface SectionDiff {
  status: 'modified' | 'unchanged' | 'added' | 'removed'
  chunks: DiffChunk[]
}

export interface StudyDiffResult {
  version_number: number
  target_version_number: number
  is_target_current: boolean
  sections: {
    title: SectionDiff
    summary: SectionDiff
    explanation: SectionDiff
    concepts: SectionDiff
    references: SectionDiff
    notes: SectionDiff
  }
}// --- Apoie o Leitorum (F0.6.6) ---

export interface SupportPublicInfo {
  pix_enabled: boolean
  pix_key: string | null
  pix_recipient_name: string | null
  pix_qr_code_url: string | null
  alternative_enabled: boolean
  alternative_label: string | null
  alternative_url: string | null
  custom_message: string | null
  has_any_method_active: boolean
}

export interface SupportAdminConfig extends SupportPublicInfo {
  source: 'database' | 'environment' | 'default'
  updated_at: string | null
  updated_by_user_id: string | null
  updated_by_name: string | null
}

export interface SupportConfigUpdate {
  pix_enabled: boolean
  pix_key?: string | null
  pix_recipient_name?: string | null
  pix_qr_code_url?: string | null
  alternative_enabled: boolean
  alternative_label?: string | null
  alternative_url?: string | null
  custom_message?: string | null
}
