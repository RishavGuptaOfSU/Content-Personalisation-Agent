import { memo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check, Copy } from 'lucide-react'

function CodeBlock({ children, className }) {
  const [copied, setCopied] = useState(false)
  const language = /language-(\w+)/.exec(className || '')?.[1]
  const raw = String(children ?? '')

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(raw.replace(/\n$/, ''))
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* clipboard blocked — nothing useful to do */
    }
  }

  return (
    <div className="group relative">
      {language && (
        <span className="absolute left-3 top-2 select-none font-mono text-[0.65rem] uppercase tracking-wider text-slate-500">
          {language}
        </span>
      )}
      <button
        type="button"
        onClick={copy}
        className="absolute right-2 top-2 rounded-md bg-slate-800/80 p-1.5 text-slate-300 opacity-0 transition-opacity hover:text-white focus-visible:opacity-100 group-hover:opacity-100"
        aria-label={copied ? 'Copied' : 'Copy code'}
      >
        {copied ? (
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
        ) : (
          <Copy className="h-3.5 w-3.5" aria-hidden="true" />
        )}
      </button>
      <pre className={language ? 'pt-7' : undefined}>
        <code className={className}>{children}</code>
      </pre>
    </div>
  )
}

const COMPONENTS = {
  a: ({ node: _node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
  pre: ({ children }) => {
    // react-markdown nests <code> inside <pre>; lift the props up so the copy
    // button and the language label can be rendered.
    const codeElement = Array.isArray(children) ? children[0] : children
    const codeProps = codeElement?.props ?? {}
    return <CodeBlock className={codeProps.className}>{codeProps.children}</CodeBlock>
  },
}

function MarkdownRenderer({ children, className = '' }) {
  return (
    <div className={`markdown ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={COMPONENTS}>
        {children || ''}
      </ReactMarkdown>
    </div>
  )
}

export default memo(MarkdownRenderer)
