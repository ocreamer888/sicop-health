"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { getNotificaciones } from "./actions";
import { NotificacionCard } from "./notificacion-card";

type Notificacion = Awaited<ReturnType<typeof getNotificaciones>>[number];

export default function AlertasPage() {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNotificaciones().then((data) => {
      setNotificaciones(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="min-h-screen">
      <div className="max-w-[1393px] mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#f9f5df] font-[family-name:var(--font-montserrat)]">
            Notificaciones
          </h1>
          <p className="text-[var(--color-text-muted)] mt-1 font-[family-name:var(--font-plus-jakarta)]">
            Nuevas licitaciones médicas de los últimos 30 días.
          </p>
        </div>

        {/* Content */}
        {loading ? (
          <div className="text-center py-24 text-[var(--color-text-muted)]">
            Cargando notificaciones...
          </div>
        ) : notificaciones.length === 0 ? (
          <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-16 text-center">
            <Bell size={48} className="mx-auto mb-4 text-[#3d4d45]" />
            <p className="text-[#f9f5df] font-medium mb-2 font-[family-name:var(--font-montserrat)]">
              Sin notificaciones
            </p>
            <p className="text-[var(--color-text-muted)] text-sm font-[family-name:var(--font-plus-jakarta)]">
              No hay nuevas licitaciones médicas en los últimos 30 días.
            </p>
          </div>
        ) : (
          <>
            <p className="text-xs text-[#5a6a62] mb-4 font-[family-name:var(--font-plus-jakarta)]">
              {notificaciones.length} licitación{notificaciones.length !== 1 ? "es" : ""} nueva{notificaciones.length !== 1 ? "s" : ""}
            </p>
            <div className="grid grid-cols-1 gap-4">
              {notificaciones.map((n) => (
                <NotificacionCard key={n.id} {...n} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
