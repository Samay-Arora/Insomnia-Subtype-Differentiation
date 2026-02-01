/**
 * PixelButton Component
 * 8-bit style button with thick blocky borders and retro hover effects
 * Used throughout the app for CTAs and form submissions
 */

import React from 'react';

interface PixelButtonProps {
    children: React.ReactNode;
    onClick?: () => void;
    type?: 'button' | 'submit' | 'reset';
    variant?: 'default' | 'primary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    className?: string;
    fullWidth?: boolean;
}

export const PixelButton: React.FC<PixelButtonProps> = ({
    children,
    onClick,
    type = 'button',
    variant = 'default',
    size = 'md',
    disabled = false,
    className = '',
    fullWidth = false,
}) => {
    const baseStyles = `
    font-pixel uppercase tracking-wider cursor-pointer
    transition-all duration-100 ease-out
    border-4 border-solid
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

    const sizeStyles = {
        sm: 'text-[8px] px-3 py-2',
        md: 'text-[10px] px-5 py-3',
        lg: 'text-xs px-8 py-4',
    };

    const variantStyles = {
        default: `
      bg-dream-purple-600 text-pixel-white border-dream-purple-400
      shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.3),inset_4px_4px_0px_0px_rgba(255,255,255,0.1),4px_4px_0px_0px_rgba(0,0,0,0.5)]
      hover:bg-dream-purple-500 hover:translate-x-[-2px] hover:translate-y-[-2px]
      hover:shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.3),inset_4px_4px_0px_0px_rgba(255,255,255,0.1),6px_6px_0px_0px_rgba(0,0,0,0.5)]
      active:translate-x-[2px] active:translate-y-[2px]
      active:shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.3),inset_4px_4px_0px_0px_rgba(255,255,255,0.1),2px_2px_0px_0px_rgba(0,0,0,0.5)]
    `,
        primary: `
      bg-dream-yellow-500 text-dream-purple-900 border-dream-yellow-300
      shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.2),inset_4px_4px_0px_0px_rgba(255,255,255,0.3),4px_4px_0px_0px_rgba(0,0,0,0.4)]
      hover:bg-dream-yellow-300 hover:translate-x-[-2px] hover:translate-y-[-2px]
      hover:shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.2),inset_4px_4px_0px_0px_rgba(255,255,255,0.3),6px_6px_0px_0px_rgba(0,0,0,0.4)]
      active:translate-x-[2px] active:translate-y-[2px]
      active:shadow-[inset_-4px_-4px_0px_0px_rgba(0,0,0,0.2),inset_4px_4px_0px_0px_rgba(255,255,255,0.3),2px_2px_0px_0px_rgba(0,0,0,0.4)]
    `,
        ghost: `
      bg-transparent text-pixel-white border-dream-purple-400
      hover:bg-dream-purple-800 hover:border-dream-purple-300
    `,
    };

    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`
        ${baseStyles}
        ${sizeStyles[size]}
        ${variantStyles[variant]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
        >
            {children}
        </button>
    );
};

export default PixelButton;
