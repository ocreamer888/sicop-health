export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[#141310] flex items-center justify-center px-4">
      {children}
    </main>
  );
}
