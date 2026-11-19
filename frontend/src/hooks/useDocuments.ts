import { useCallback, useEffect, useState } from "react";
import { deleteDoc, errorMessage, listDocs, uploadDoc } from "../api/client";
import type { DocInfo } from "../types";

export function useDocuments() {
  const [docs, setDocs] = useState<DocInfo[]>([]);
  const [status, setStatus] = useState("");

  const refresh = useCallback(async () => {
    try {
      setDocs(await listDocs());
    } catch (e) {
      setStatus(errorMessage(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const upload = useCallback(
    async (files: File[]) => {
      for (const file of files) {
        setStatus(`Reading ${file.name}…`);
        try {
          await uploadDoc(file);
        } catch (e) {
          setStatus(errorMessage(e));
          await refresh();
          return;
        }
      }
      setStatus("Ready. Ask away.");
      await refresh();
    },
    [refresh],
  );

  const remove = useCallback(
    async (name: string) => {
      try {
        await deleteDoc(name);
      } catch (e) {
        setStatus(errorMessage(e));
      }
      await refresh();
    },
    [refresh],
  );

  return { docs, status, upload, remove };
}
