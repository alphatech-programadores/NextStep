import { useEffect, RefObject } from 'react';

type AnyEvent = MouseEvent | TouchEvent;

// Esta es la firma genérica correcta.
// Aceptará una referencia a cualquier tipo de elemento que sea un HTMLElement (div, button, etc.)
export function useOnClickOutside<T extends HTMLElement>(
    ref: RefObject<T>,
    handler: (event: AnyEvent) => void
): void {
    useEffect(() => {
        const listener = (event: AnyEvent) => {
            // El elemento referenciado
            const el = ref?.current;

            // Si el elemento no existe o el clic fue dentro de él, no hagas nada
            if (!el || el.contains(event.target as Node)) {
                return;
            }

            // Si el clic fue afuera, ejecuta el handler
            handler(event);
        };

        document.addEventListener('mousedown', listener);
        document.addEventListener('touchstart', listener);

        return () => {
            document.removeEventListener('mousedown', listener);
            document.removeEventListener('touchstart', listener);
        };
    }, [ref, handler]);
}