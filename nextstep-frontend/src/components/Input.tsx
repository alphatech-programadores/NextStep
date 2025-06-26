'use client';

import React from 'react';

interface InputProps {
    label: string;
    name: string;
    type: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    required?: boolean;
    placeholder?: string;
}

export default function Input({ label, name, type, required, placeholder = 'text', value, onChange }: InputProps) {
    return (
        <div className="form-group">
            <label htmlFor={name}>{label}</label>
            <input
                id={name}
                name={name}
                type={type}
                value={value}
                onChange={onChange}
                className="form-control"
                required={required}
                placeholder={placeholder}
            />
        </div>
    );
}
