"use client";

import { useEffect } from "react";
import { recordLicitacionView } from "./record-activity";

export function ActivityRecorder({
  instcartelno,
  instCode,
  biddocStartDt,
  instnm,
}: {
  instcartelno: string;
  instCode: string | null;
  biddocStartDt: string | null;
  instnm: string | null;
}) {
  useEffect(() => {
    recordLicitacionView(instcartelno, instCode, biddocStartDt, instnm);
  }, [instcartelno, instCode, biddocStartDt, instnm]);

  return null;
}
