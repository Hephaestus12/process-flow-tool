// app/api/proxy/[...path]/route.ts
import { NextResponse } from "next/server";
import axios from "axios";

// Force this route to be dynamic so that dynamic params can be awaited.
export const dynamic = "force-dynamic";

const BASE_URL = process.env.EXTERNAL_API_BASE_URL; // e.g., "https://external-api.example.com"
const API_KEY = process.env.EXTERNAL_API_KEY; // Your secret API key

if (!BASE_URL || !API_KEY) {
  throw new Error(
    "Missing EXTERNAL_API_BASE_URL or EXTERNAL_API_KEY in environment variables."
  );
}

async function forwardRequest(
  method: "GET" | "POST" | "PUT" | "DELETE",
  request: Request,
  path: string[]
) {
  const urlPath = path.join("/");
  const requestUrl = new URL(request.url);
  const queryString = requestUrl.search;
  const targetUrl = `${BASE_URL}/${urlPath}${queryString}`;

  const headers: Record<string, string> = {
    "x-api-key": API_KEY,
  };

  let data;
  if (method === "POST" || method === "PUT") {
    data = await request.json();
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await axios({
      method,
      url: targetUrl,
      headers,
      data,
    });
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error("Error in proxy:", error.message);
    return NextResponse.json(
      { error: error.message },
      { status: error.response?.status || 500 }
    );
  }
}

export async function GET(
  request: Request,
  context: { params: { path: string[] } }
) {
  // Await the dynamic params before using them.
  const { params } = await Promise.resolve(context);
  return forwardRequest("GET", request, params.path);
}

export async function POST(
  request: Request,
  context: { params: { path: string[] } }
) {
  const { params } = await Promise.resolve(context);
  return forwardRequest("POST", request, params.path);
}

export async function PUT(
  request: Request,
  context: { params: { path: string[] } }
) {
  const { params } = await Promise.resolve(context);
  return forwardRequest("PUT", request, params.path);
}

export async function DELETE(
  request: Request,
  context: { params: { path: string[] } }
) {
  const { params } = await Promise.resolve(context);
  return forwardRequest("DELETE", request, params.path);
}
