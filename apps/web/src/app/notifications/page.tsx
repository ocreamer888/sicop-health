"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { getNotificaciones, getReadIds, markNotificacionRead } from "./actions";
import { NotificacionCard } from "./notificacion-card";

type Notificacion = Awaited<ReturnType<typeof getNotificaciones>>[number];

export default function AlertasPage() {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [readIds, setReadIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getNotificaciones(), getReadIds()]).then(([notifs, reads]) => {
      setNotificaciones(notifs);
      setReadIds(reads);
      setLoading(false);
    });
  }, []);

  const unreadCount = notificaciones.filter(n => !readIds.includes(n.id)).length;

  const handleMarkRead = async (id: string) => {
    await markNotificacionRead(id);
    setReadIds(prev => [...prev, id]);
  };

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
          <div className="rounded-[24px] bg-[#2c3833] border border-[#3d4d45] p-12 text-center">
            <div className="text-4xl mb-4">🎯</div>
            <p className="text-[#f9f5df] font-semibold mb-1 font-[family-name:var(--font-montserrat)]">
              Tu radar está activo
            </p>
            <p className="text-[var(--color-text-muted)] text-sm mb-4 font-[family-name:var(--font-plus-jakarta)]">
              Monitoreando todas las licitaciones médicas de SICOP
            </p>
            <p className="text-xs text-[#5a6a62]">
              Las nuevas oportunidades aparecerán aquí en cuanto sean publicadas.
            </p>
          </div>
        ) : (
          <>
            {/* Unread banner */}
            {unreadCount > 0 && (
              <div className="rounded-[24px] bg-[#84a584]/10 border border-[#84a584]/30 p-4 mb-6">
                <p className="text-sm text-[#84a584] font-medium">
                  🔔 {unreadCount} nueva{unreadCount !== 1 ? "s" : ""} oportunidad{unreadCount !== 1 ? "es" : ""} por revisar
                </p>
              </div>
            )}
            <p className="text-xs text-[#5a6a62] mb-4 font-[family-name:var(--font-plus-jakarta)]">
              {notificaciones.length} licitación{notificaciones.length !== 1 ? "es" : ""} nueva{notificaciones.length !== 1 ? "s" : ""}
              {unreadCount > 0 && ` · ${unreadCount} sin leer`}
            </p>
            <div className="grid grid-cols-1 gap-4">
              {notificaciones.map((n) => (
                <NotificacionCard
                  key={n.id}
                  {...n}
                  isUnread={!readIds.includes(n.id)}
                  onRead={() => handleMarkRead(n.id)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
