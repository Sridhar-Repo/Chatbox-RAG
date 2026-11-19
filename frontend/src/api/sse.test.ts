import { describe, expect, it } from "vitest";
import { readSSE } from "./sse";

function streamOf(...parts: string[]): ReadableStream<Uint8Array> {
  const enc = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      parts.forEach((p) => controller.enqueue(enc.encode(p)));
      controller.close();
    },
  });
}

async function collect<T>(gen: AsyncGenerator<T>): Promise<T[]> {
  const out: T[] = [];
  for await (const item of gen) out.push(item);
  return out;
}

describe("readSSE", () => {
  it("parses several events from one chunk", async () => {
    const body = streamOf('data: {"type":"token","data":"Hi"}\n\ndata: {"type":"done","data":null}\n\n');
    expect(await collect(readSSE(body))).toEqual([
      { type: "token", data: "Hi" },
      { type: "done", data: null },
    ]);
  });

  it("handles an event split across chunks", async () => {
    const body = streamOf('data: {"type":"tok', 'en","data":"Hello"}\n', '\ndata: {"type":"done","data":null}\n\n');
    expect(await collect(readSSE(body))).toEqual([
      { type: "token", data: "Hello" },
      { type: "done", data: null },
    ]);
  });

  it("keeps multi-byte characters intact when split mid-character", async () => {
    const bytes = new TextEncoder().encode('data: {"type":"token","data":"₹5"}\n\n');
    const body = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(bytes.slice(0, 30));
        c.enqueue(bytes.slice(30));
        c.close();
      },
    });
    expect(await collect(readSSE(body))).toEqual([{ type: "token", data: "₹5" }]);
  });

  it("ignores empty frames", async () => {
    expect(await collect(readSSE(streamOf("\n\n\n\n")))).toEqual([]);
  });
});
