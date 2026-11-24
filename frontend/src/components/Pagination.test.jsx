import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Pagination, { PAGE_SIZE } from './Pagination'

describe('Pagination', () => {
  const result = {
    page: 1,
    count: 45,
    results: Array.from({ length: 20 }, (_, i) => ({ id: i + 1 })),
  }

  it('uses page size of 20', () => {
    expect(PAGE_SIZE).toBe(20)
  })

  it('disables Previous on the first page', () => {
    render(
      <Pagination
        result={result}
        loading={false}
        onPage={vi.fn()}
        label="Search results"
      />,
    )

    expect(
      screen.getByRole('button', { name: /Prev/ }),
    ).toBeDisabled()
  })

  it('calls onPage with the next page when Next is clicked', async () => {
    const user = userEvent.setup()
    const onPage = vi.fn()

    render(
      <Pagination
        result={result}
        loading={false}
        onPage={onPage}
        label="Search results"
      />,
    )

    await user.click(screen.getByRole('button', { name: /Next/ }))

    expect(onPage).toHaveBeenCalledWith(2)
  })

  it('disables both buttons while loading', () => {
    render(
      <Pagination
        result={result}
        loading={true}
        onPage={vi.fn()}
        label="Search results"
      />,
    )

    expect(screen.getByRole('button', { name: /Prev/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /Next/ })).toBeDisabled()
  })
})