export interface DocInfo {
  name: string;
  chunks: number;
}

export interface Source {
  n: number;
  source: string;
  page: number; // 0 = no page info
  text: string;
  score: number; // 0..1
}

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export type ChatEvent =
  | { type: "sources"; data: Source[] }
  | { type: "token"; data: string }
  | { type: "error"; data: string }
  | { type: "done"; data: null };

export interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: Source[];
  status: "streaming" | "done" | "error";
}
