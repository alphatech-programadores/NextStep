// src/components/Input.tsx

import { kMaxLength } from 'buffer';
import React from 'react';

// Define la interfaz de las propiedades que tu componente FormInput puede recibir
interface FormInputProps {
    label?: string;
    name: string;
    type: string; // 'text', 'email', 'password', 'number', 'textarea', etc.
    value: string | number;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void; // Aceptar ambos tipos de eventos
    className?: string;
    required?: boolean;
    placeholder?: string;
    readOnly?: boolean;
    step?: string; // Útil para inputs tipo 'number'
    disabled?: boolean; // Añadido para flexibilidad    
    maxLength?: number;
}

const FormInput: React.FC<FormInputProps> = ({
    label,
    name,
    type,
    value,
    onChange,
    className,
    required,
    placeholder,
    readOnly,
    step,
    disabled,
    maxLength,
}) => {
    // Determinar qué elemento renderizar basado en el tipo
    const InputElement = type === 'textarea' ? 'textarea' : 'input';

    return (
        <div className={`${className} ${type === 'textarea' ? 'textarea-container' : ''}`}>
            {label && <label htmlFor={name}>{label}</label>}
            <InputElement
                id={name}
                name={name}
                type={type !== 'textarea' ? type : undefined} // No pasar 'type' a textarea
                value={value}
                onChange={onChange}
                className={className} // Aplicaremos estilos comunes a todos los inputs
                required={required}
                placeholder={placeholder}
                step={step}
                readOnly={readOnly}
                disabled={disabled}
                maxLength={kMaxLength}
                // Si es un textarea, puedes añadir props específicas como rows, cols
                {...(type === 'textarea' && { rows: 5 })}
            />
        </div>
    );
};

export default FormInput;