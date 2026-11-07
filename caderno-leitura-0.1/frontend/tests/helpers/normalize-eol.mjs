// Testes que procuram trechos de código-fonte com quebras de linha ficam indiferentes a CRLF/LF.
// No Windows, um checkout com core.autocrlf pode converter só os arquivos tocados, e o mesmo teste passava num
// checkout e falhava em outro (fecho do lote 2 do 0.10, 2026-11-07). Importar este módulo primeiro no teste.
import fs from 'node:fs'
import { syncBuiltinESMExports } from 'node:module'

const readFileSyncRaw = fs.readFileSync

if (!readFileSyncRaw.__normalizesEol) {
  const normalized = (...args) => {
    const content = readFileSyncRaw(...args)
    return typeof content === 'string' ? content.replace(/\r\n/g, '\n') : content
  }
  normalized.__normalizesEol = true
  fs.readFileSync = normalized
  // Atualiza também `import { readFileSync } from 'node:fs'`.
  syncBuiltinESMExports()
}
