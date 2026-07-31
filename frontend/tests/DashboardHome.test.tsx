import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DashboardHome from '@/app/(dashboard)/page';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => '/',
}));

describe('DashboardHome', () => {
  it('renders the dashboard header', () => {
    render(<DashboardHome />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders KPI cards', () => {
    render(<DashboardHome />);
    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('Avg Margin')).toBeInTheDocument();
    expect(screen.getByText('Forecast Accuracy')).toBeInTheDocument();
    expect(screen.getByText('Active Alerts')).toBeInTheDocument();
  });
});
