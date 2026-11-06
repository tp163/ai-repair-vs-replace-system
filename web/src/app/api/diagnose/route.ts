import { inputSchema } from '@/lib/contracts';
import { phones } from '@/lib/catalogue';
import { runAgents } from '@/lib/agents';
export const runtime='nodejs';
export async function POST(request:Request){
 if(request.headers.get('origin')&&request.headers.get('origin')!==new URL(request.url).origin)return Response.json({error:'Origin not allowed'},{status:403});
 try{
  const reader=request.body?.getReader();if(!reader)return Response.json({error:'Missing request'},{status:400});
  const chunks:Uint8Array[]=[];let length=0;
  while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>3000000){await reader.cancel();return Response.json({error:'Upload must be under 2 MB'},{status:413});}chunks.push(value);}
  const parsed=inputSchema.safeParse(JSON.parse(Buffer.concat(chunks).toString()));
  if(!parsed.success)return Response.json({error:'Confirm the device and provide a valid description and budget.'},{status:400});
  if(!phones.some(p=>p.id===parsed.data.deviceId))return Response.json({error:'Unknown device variant'},{status:400});
  return Response.json(await runAgents(parsed.data));
 }catch{return Response.json({error:'Unable to assess this request. Please try again.'},{status:500});}
}
