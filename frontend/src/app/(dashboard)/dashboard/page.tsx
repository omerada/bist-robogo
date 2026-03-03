/**
 * Dashboard sayfası — tüm kritik bilgilerin tek bakışta görüldüğü ana ekran.
 * useDashboardSummary hook'u ile tek API çağrısında tüm veriyi çeker.
 */

import type { Metadata } from "next";
import { DashboardContent } from "./_components/dashboard-content";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return <DashboardContent />;
}
