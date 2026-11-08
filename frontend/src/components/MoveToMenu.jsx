import { useEffect, useRef, useState } from 'react'

export default function MoveToMenu({ collections, currentId, disabled, onMove }) {
  const [open, setOpen] = useState(false)
  const button = useRef(null)
  const menu = useRef(null)
  const others = collections.filter((collection) => collection.id !== currentId)

  function close({ focusButton = true } = {}) {
    setOpen(false)
    if (focusButton) {
      button.current.focus()
    }
  }

  useEffect(() => {
    if (!open) {
      return undefined
    }
    menu.current.querySelector('[role=menuitem]')?.focus()
    function handlePointer(event) {
      if (!menu.current.contains(event.target) && !button.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handlePointer)
    return () => document.removeEventListener('mousedown', handlePointer)
  }, [open])

  function handleKeyDown(event) {
    const items = [...menu.current.querySelectorAll('[role=menuitem]')]
    const index = items.indexOf(document.activeElement)
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
    } else if (event.key === 'ArrowDown' && items.length) {
      event.preventDefault()
      items[(index + 1) % items.length].focus()
    } else if (event.key === 'ArrowUp' && items.length) {
      event.preventDefault()
      items[(index - 1 + items.length) % items.length].focus()
    } else if (event.key === 'Tab') {
      close({ focusButton: false })
    }
  }

  return (
    <div className="relative">
      <button
        ref={button}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        disabled={disabled}
        onClick={() => setOpen(!open)}
        className="rounded-md border border-gray-300 bg-white px-4 py-2 font-medium whitespace-nowrap hover:bg-gray-100 disabled:opacity-50"
      >
        Move to… ▾
      </button>
      {open && (
        <div
          ref={menu}
          role="menu"
          aria-label="Move to collection"
          onKeyDown={handleKeyDown}
          className="absolute left-0 z-10 mt-1 max-h-72 w-56 sm:right-0 sm:left-auto overflow-y-auto rounded-md border border-gray-300 bg-white py-1 shadow-lg"
        >
          {others.length === 0 ? (
            <p className="px-4 py-2 text-gray-500">No other collections</p>
          ) : (
            others.map((collection) => (
              <button
                key={collection.id}
                type="button"
                role="menuitem"
                onClick={() => {
                  close()
                  onMove(collection)
                }}
                className="block w-full px-4 py-2 text-left break-words hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
              >
                {collection.name}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}
