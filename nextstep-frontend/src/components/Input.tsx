// src/components/Input.tsx

import React from 'react';

// Define la interfaz de las propiedades que tu componente FormInput puede recibir
interface FormInputProps {
    label?: string; // Hacemos el label opcional para campos sin label visual (ej. en búsquedas)
    name: string;
    type: string;
    value: string | number;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;

    // ¡Añade esta línea para className!
    className?: string; // Permite pasar clases CSS desde el componente padre

    // Props que ya habíamos añadido o que son útiles:
    required?: boolean; // Para el atributo 'required' de HTML
    placeholder?: string; // Para el atributo 'placeholder' de HTML
    readOnly?: boolean;
    step?: string;
    // Puedes añadir más props de HTML si las necesitas, por ejemplo:
    // disabled?: boolean;
    // readOnly?: boolean;
}

const FormInput: React.FC<FormInputProps> = ({
    label,
    name,
    type,
    value,
    onChange,
    className, // ¡Desestructura la prop 'className' aquí!
    required,
    placeholder,
    readOnly,
    step,

    // ...desestructura cualquier otra prop que añadas
}) => {
    return (
        <div>
            {/* Solo renderiza el label si se proporciona */}
            {label && <label htmlFor={name}>{label}</label>}
            <input
                id={name}
                name={name}
                type={type}
                value={value}
                onChange={onChange}
                className={className} // ¡Pasa la prop 'className' al elemento <input> HTML!
                required={required}
                placeholder={placeholder}
                step={step}
                readOnly={readOnly}
            // ...pasa cualquier otra prop al <input>
            />
        </div>
    );
};

export default FormInput;