/**
 * PixelInput Component
 * Form input with retro styling for auth forms
 * Features pixel borders and dreamy color scheme
 */

import React from 'react';

interface PixelInputProps {
    type?: 'text' | 'email' | 'password';
    placeholder?: string;
    value: string;
    onChange: (value: string) => void;
    label?: string;
    name?: string;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

export const PixelInput: React.FC<PixelInputProps> = ({
    type = 'text',
    placeholder,
    value,
    onChange,
    label,
    name,
    required = false,
    disabled = false,
    className = '',
}) => {
    return (
        <div className={`w-full ${className}`}>
            {label && (
                <label
                    htmlFor={name}
                    className="block font-pixel text-[8px] text-dream-yellow-500 uppercase tracking-wider mb-2"
                >
                    {label}
                    {required && <span className="text-dream-yellow-300 ml-1">*</span>}
                </label>
            )}
            <input
                type={type}
                id={name}
                name={name}
                placeholder={placeholder}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                required={required}
                disabled={disabled}
                className={`
          w-full px-4 py-3
          font-body text-sm text-pixel-white
          bg-dream-indigo-800 
          border-4 border-dream-purple-500
          placeholder:text-dream-purple-400
          focus:outline-none focus:border-dream-yellow-500
          disabled:opacity-50 disabled:cursor-not-allowed
          shadow-[inset_-3px_-3px_0px_0px_rgba(0,0,0,0.3),inset_3px_3px_0px_0px_rgba(255,255,255,0.05)]
          transition-colors duration-150
        `}
            />
        </div>
    );
};

export default PixelInput;
