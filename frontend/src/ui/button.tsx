import type { ReactNode } from 'react'
export default function Button({ children }: { children: ReactNode }) { 
  return (
    <button className="bg-gray-950 p-2 m-2 text-white text-sm border-gray-300" >
      { children }
    </button>
  );
}
