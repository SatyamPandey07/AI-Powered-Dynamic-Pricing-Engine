'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import { TrendingUp, DollarSign, Activity, AlertCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';

// Mock data for charts
const priceData = [
  { date: 'Jul 1', yourPrice: 50, competitorAvg: 48 },
  { date: 'Jul 5', yourPrice: 48, competitorAvg: 48 },
  { date: 'Jul 10', yourPrice: 49, competitorAvg: 47 },
  { date: 'Jul 15', yourPrice: 45, competitorAvg: 46 },
  { date: 'Jul 20', yourPrice: 46, competitorAvg: 45 },
  { date: 'Jul 25', yourPrice: 48, competitorAvg: 48 },
  { date: 'Jul 30', yourPrice: 52, competitorAvg: 50 },
];

const revenueData = [
  { date: 'Jul 1', revenue: 4000 },
  { date: 'Jul 5', revenue: 4200 },
  { date: 'Jul 10', revenue: 3800 },
  { date: 'Jul 15', revenue: 5100 },
  { date: 'Jul 20', revenue: 4900 },
  { date: 'Jul 25', revenue: 5500 },
  { date: 'Jul 30', revenue: 6200 },
];

const recommendations = [
  { id: 1, sku: 'B08F22K', current: 49.99, recommended: 45.99, impact: '+$1,200', status: 'pending' },
  { id: 2, sku: 'C99X100', current: 15.00, recommended: 17.50, impact: '+$400', status: 'accepted' },
  { id: 3, sku: 'A11P002', current: 120.00, recommended: 110.00, impact: '+$2,500', status: 'pending' },
];

const alerts = [
  { id: 1, message: 'Competitor X dropped price on SKU B08F22K by 10%', type: 'warning' },
  { id: 2, message: 'Forecast accuracy for category Electronics dropped below 80%', type: 'error' },
];

export default function DashboardHome() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground">Overview of your pricing engine performance.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$45,231.89</div>
            <p className="text-xs text-muted-foreground flex items-center text-emerald-500 mt-1">
              <ArrowUpRight className="h-3 w-3 mr-1" /> +20.1% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Margin</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42.5%</div>
            <p className="text-xs text-muted-foreground flex items-center text-emerald-500 mt-1">
              <ArrowUpRight className="h-3 w-3 mr-1" /> +2.4% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Forecast Accuracy</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">92.4%</div>
            <p className="text-xs text-muted-foreground flex items-center text-emerald-500 mt-1">
              <ArrowUpRight className="h-3 w-3 mr-1" /> Target: {'>'}90%
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alerts.length}</div>
            <p className="text-xs text-muted-foreground flex items-center text-amber-500 mt-1">
              Requires attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Revenue Trend (Last 30 Days)</CardTitle>
            <CardDescription>Daily revenue generated across all SKUs.</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
                  <Tooltip formatter={(value) => [`$${value}`, "Revenue"]} />
                  <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Price Competitiveness</CardTitle>
            <CardDescription>Your price vs market average.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="yourPrice" name="Your Price" stroke="#10b981" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="competitorAvg" name="Competitor Avg" stroke="#f43f5e" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Recommendations</CardTitle>
            <CardDescription>Top price optimization recommendations based on latest data.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Current</TableHead>
                  <TableHead>Recommended</TableHead>
                  <TableHead>Est. Impact</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recommendations.map((rec) => (
                  <TableRow key={rec.id}>
                    <TableCell className="font-medium">{rec.sku}</TableCell>
                    <TableCell>${rec.current.toFixed(2)}</TableCell>
                    <TableCell className="text-emerald-600 font-semibold">${rec.recommended.toFixed(2)}</TableCell>
                    <TableCell>{rec.impact}</TableCell>
                    <TableCell>
                      <Badge variant={rec.status === 'pending' ? 'secondary' : 'default'}>
                        {rec.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      {rec.status === 'pending' && (
                        <>
                          <Button size="sm" variant="default">Accept</Button>
                          <Button size="sm" variant="outline">Review</Button>
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Top Alerts</CardTitle>
            <CardDescription>System alerts and notifications.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-start space-x-4 border-b pb-4 last:border-0 last:pb-0">
                  <div className={`mt-1 h-2 w-2 rounded-full ${alert.type === 'error' ? 'bg-red-500' : 'bg-amber-500'}`} />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{alert.message}</p>
                    <p className="text-xs text-muted-foreground">Just now</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
