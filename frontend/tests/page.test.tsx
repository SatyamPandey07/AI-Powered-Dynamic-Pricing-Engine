import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Home from '../src/app/page'

describe('Home Page', () => {
  it('renders the heading', () => {
    render(<Home />)
    const heading = screen.getByText(/Dynamic Pricing Engine/i)
    expect(heading).toBeDefined()
  })
})
