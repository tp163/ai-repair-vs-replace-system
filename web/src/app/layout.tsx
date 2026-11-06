import type { Metadata } from 'next';
import './globals.css';
import './reference-theme.css';
export const metadata:Metadata={title:'REVIVAI · A smarter next move',description:'Evidence-aware phone diagnosis and replacement exploration.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>;}
