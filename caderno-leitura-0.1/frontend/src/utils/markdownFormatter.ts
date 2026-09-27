export type MarkdownFormatAction =
  | 'bold'
  | 'italic'
  | 'heading'
  | 'bullet_list'
  | 'quote'
  | 'code'
  | 'link'

export interface MarkdownFormatResult {
  newText: string
  newSelectionStart: number
  newSelectionEnd: number
}

export function formatMarkdown(
  text: string,
  selectionStart: number,
  selectionEnd: number,
  action: MarkdownFormatAction,
): MarkdownFormatResult {
  const start = Math.min(selectionStart, selectionEnd)
  const end = Math.max(selectionStart, selectionEnd)
  const hasSelection = start !== end
  const selected = text.slice(start, end)

  if (action === 'bold') {
    if (hasSelection) {
      // Se já está envolvido por **, desfaz
      if (
        start >= 2 &&
        end <= text.length - 2 &&
        text.slice(start - 2, start) === '**' &&
        text.slice(end, end + 2) === '**'
      ) {
        return {
          newText: text.slice(0, start - 2) + selected + text.slice(end + 2),
          newSelectionStart: start - 2,
          newSelectionEnd: end - 2,
        }
      }
      return {
        newText: text.slice(0, start) + '**' + selected + '**' + text.slice(end),
        newSelectionStart: start + 2,
        newSelectionEnd: end + 2,
      }
    }
    const placeholder = 'texto em negrito'
    return {
      newText: text.slice(0, start) + '**' + placeholder + '**' + text.slice(end),
      newSelectionStart: start + 2,
      newSelectionEnd: start + 2 + placeholder.length,
    }
  }

  if (action === 'italic') {
    if (hasSelection) {
      if (
        start >= 1 &&
        end <= text.length - 1 &&
        text.slice(start - 1, start) === '*' &&
        text.slice(end, end + 1) === '*' &&
        text.slice(start - 2, start) !== '**'
      ) {
        return {
          newText: text.slice(0, start - 1) + selected + text.slice(end + 1),
          newSelectionStart: start - 1,
          newSelectionEnd: end - 1,
        }
      }
      return {
        newText: text.slice(0, start) + '*' + selected + '*' + text.slice(end),
        newSelectionStart: start + 1,
        newSelectionEnd: end + 1,
      }
    }
    const placeholder = 'texto em itálico'
    return {
      newText: text.slice(0, start) + '*' + placeholder + '*' + text.slice(end),
      newSelectionStart: start + 1,
      newSelectionEnd: start + 1 + placeholder.length,
    }
  }

  if (action === 'code') {
    if (hasSelection) {
      return {
        newText: text.slice(0, start) + '`' + selected + '`' + text.slice(end),
        newSelectionStart: start + 1,
        newSelectionEnd: end + 1,
      }
    }
    const placeholder = 'código'
    return {
      newText: text.slice(0, start) + '`' + placeholder + '`' + text.slice(end),
      newSelectionStart: start + 1,
      newSelectionEnd: start + 1 + placeholder.length,
    }
  }

  if (action === 'link') {
    if (hasSelection) {
      const inserted = `[${selected}](https://...)`
      return {
        newText: text.slice(0, start) + inserted + text.slice(end),
        newSelectionStart: start + selected.length + 3,
        newSelectionEnd: start + inserted.length - 1,
      }
    }
    const label = 'texto do link'
    const inserted = `[${label}](https://...)`
    return {
      newText: text.slice(0, start) + inserted + text.slice(end),
      newSelectionStart: start + 1,
      newSelectionEnd: start + 1 + label.length,
    }
  }

  if (action === 'heading') {
    const lineStart = text.lastIndexOf('\n', start - 1) + 1
    const lineEndIndex = text.indexOf('\n', start)
    const lineEnd = lineEndIndex === -1 ? text.length : lineEndIndex
    const currentLine = text.slice(lineStart, lineEnd)

    let newLine = currentLine
    let offsetDiff = 0

    if (currentLine.startsWith('### ')) {
      // Toggle off
      newLine = currentLine.slice(4)
      offsetDiff = -4
    } else if (currentLine.startsWith('## ')) {
      newLine = '### ' + currentLine.slice(3)
      offsetDiff = 1
    } else if (currentLine.startsWith('# ')) {
      newLine = '### ' + currentLine.slice(2)
      offsetDiff = 2
    } else {
      newLine = '### ' + currentLine
      offsetDiff = 4
    }

    return {
      newText: text.slice(0, lineStart) + newLine + text.slice(lineEnd),
      newSelectionStart: Math.max(lineStart, start + offsetDiff),
      newSelectionEnd: Math.max(lineStart, end + offsetDiff),
    }
  }

  if (action === 'bullet_list' || action === 'quote') {
    const prefix = action === 'bullet_list' ? '- ' : '> '
    const lineStart = text.lastIndexOf('\n', start - 1) + 1
    const lineEndIndex = text.indexOf('\n', end)
    const lineEnd = lineEndIndex === -1 ? text.length : lineEndIndex
    const block = text.slice(lineStart, lineEnd)
    const lines = block.split('\n')

    const allHavePrefix = lines.every((l) => l.startsWith(prefix) || !l.trim())

    let modifiedLines: string[]
    let diff = 0
    if (allHavePrefix) {
      modifiedLines = lines.map((l) => {
        if (l.startsWith(prefix)) {
          diff -= prefix.length
          return l.slice(prefix.length)
        }
        return l
      })
    } else {
      modifiedLines = lines.map((l) => {
        if (l.trim()) {
          diff += prefix.length
          return prefix + l
        }
        return l
      })
    }

    const newBlock = modifiedLines.join('\n')
    return {
      newText: text.slice(0, lineStart) + newBlock + text.slice(lineEnd),
      newSelectionStart: Math.max(lineStart, start + (allHavePrefix ? -prefix.length : prefix.length)),
      newSelectionEnd: Math.max(lineStart, end + diff),
    }
  }

  return {
    newText: text,
    newSelectionStart: start,
    newSelectionEnd: end,
  }
}

export function applyFormatToTextarea(
  textarea: HTMLTextAreaElement,
  action: MarkdownFormatAction,
): void {
  const { newText, newSelectionStart, newSelectionEnd } = formatMarkdown(
    textarea.value,
    textarea.selectionStart,
    textarea.selectionEnd,
    action,
  )
  textarea.value = newText
  textarea.dispatchEvent(new Event('input', { bubbles: true }))
  textarea.focus()
  textarea.setSelectionRange(newSelectionStart, newSelectionEnd)
}
