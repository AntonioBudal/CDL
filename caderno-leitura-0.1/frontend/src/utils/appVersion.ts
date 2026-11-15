/**
 * F0.12.01 (spec 114): versão do app no padrão Versionamento Semântico 2.0.0.
 *
 * Roadmap fechado `0.MINOR.0`; em andamento `0.MINOR.0-alpha.N` (N = features do roadmap entregues); correção depois
 * de fechado `0.MINOR.PATCH`. Fonte única: `caderno-leitura-0.1/VERSION`, embutido no build como `__APP_VERSION__`.
 */

// Expressão oficial do semver.org (sem grupos nomeados).
const SEMVER = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/

export interface Semver {
  major: number
  minor: number
  patch: number
  prerelease: string | null
  build: string | null
}

export function parseSemver(value: string): Semver | null {
  const match = SEMVER.exec((value || '').trim())
  if (!match) return null
  return {
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3]),
    prerelease: match[4] ?? null,
    build: match[5] ?? null,
  }
}

export function isValidSemver(value: string): boolean {
  return parseSemver(value) !== null
}

/** "0.12" — o roadmap da versão. */
export function roadmapOf(value: string): string {
  const v = parseSemver(value)
  return v ? `${v.major}.${v.minor}` : ''
}

/** Versão com o commit da compilação como metadado de build (`0.12.0-alpha.1+a1b2c3d`), quando houver commit. */
export function fullVersion(version: string, commit: string | null | undefined): string {
  const clean = (commit || '').trim()
  if (!clean || clean === 'desconhecido' || !/^[0-9a-zA-Z-]+$/.test(clean)) return version
  return `${version}+${clean}`
}

/** Versão embutida no build (ou reserva, em testes fora do Vite). */
export function appVersion(): string {
  return typeof __APP_VERSION__ === 'string' && __APP_VERSION__ ? __APP_VERSION__ : '0.0.0-desconhecida'
}

export function buildCommit(): string {
  return typeof __BUILD_COMMIT__ === 'string' ? __BUILD_COMMIT__ : ''
}
