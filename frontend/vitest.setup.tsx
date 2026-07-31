import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Recharts to avoid DOM measurement errors in JSDOM
vi.mock('recharts', async () => {
  const OriginalRechartsModule = await vi.importActual('recharts');
  return {
    ...OriginalRechartsModule,
    ResponsiveContainer: ({ children }: any) => (
      <div style={{ width: 800, height: 600 }}>{children}</div>
    ),
  };
});
