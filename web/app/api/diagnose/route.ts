import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return NextResponse.json({ error: 'Enter your device details and symptoms.' }, { status: 400 });
  }

  const backendUrl = process.env.DIAGNOSIS_BACKEND_URL || 'http://127.0.0.1:8000';
  try {
    const pythonRes = await fetch(new URL('/api/diagnose', backendUrl), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    return new Response(pythonRes.body, {
      status: pythonRes.status,
      headers: { 'Content-Type': pythonRes.headers.get('content-type') ?? 'application/json' },
    });
  } catch {
    return NextResponse.json({ error: 'Could not reach the diagnosis backend. Check that it is running and try again.' }, { status: 502 });
  }
}
