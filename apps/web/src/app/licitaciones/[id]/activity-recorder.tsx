"use client";

import { useEffect } from "react";
import { recordLicitacionView } from "./record-activity";

export function ActivityRecorder({
  instcartelno,
  instCode,
  biddocStartDt,
}: {
  instcartelno: string;
  instCode: string | null;
  biddocStartDt: string | null;
}) {
  useEffect(() => {
    recordLicitacionView(instcartelno, instCode, biddocStartDt);
  }, [instcartelno, instCode, biddocStartDt]);

  return null;
}
