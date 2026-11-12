import type { ReactNode } from 'react'
export default function Button({ children }: { children: ReactNode }) { 
  return (
    <button className="bg-gray-800 hover:bg-gray-700 p-2 m-2 text-white text-sm border border-gray-700" >
      { children }
    </button>
  );
}
