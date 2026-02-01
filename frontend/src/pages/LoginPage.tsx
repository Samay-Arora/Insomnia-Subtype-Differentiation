/**
 * LoginPage Component
 * Retro game-style login form
 * "Enter your name, traveler" aesthetic for authentication
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PixelButton, PixelCard, PixelInput } from '../components/ui';
import { StarryBackground } from '../components/background';

interface LoginPageProps {
    onLogin?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const { login } = await import('../services/api');
            const result = await login({ email, password });

            if (result.success) {
                // Auth state listener in App.tsx will handle redirect
                onLogin?.();
            } else {
                alert(result.error || 'Login failed');
            }
        } catch (error) {
            console.error(error);
            alert('Login error');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-dream-indigo-900 via-dream-purple-900 to-dream-purple-800 relative flex items-center justify-center p-4">
            <StarryBackground starCount={40} />

            <div className="relative z-10 w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <Link to="/" className="inline-block mb-6">
                        <span className="font-pixel text-[10px] text-dream-purple-400 hover:text-dream-purple-300 transition-colors">
                            ← BACK TO HOME
                        </span>
                    </Link>

                    <h1 className="font-pixel text-xl text-pixel-white mb-2">
                        WELCOME BACK
                    </h1>
                    <p className="font-pixel text-[10px] text-dream-yellow-500">
                        ENTER YOUR CREDENTIALS
                    </p>
                </div>

                {/* Login Form */}
                <PixelCard variant="dark">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Decorative header */}
                        <div className="flex justify-center mb-6">
                            <div className="flex gap-1">
                                {['💤', '🌙', '⭐'].map((emoji, i) => (
                                    <span
                                        key={i}
                                        className="text-2xl"
                                        style={{
                                            animation: 'float 2s ease-in-out infinite',
                                            animationDelay: `${i * 0.3}s`,
                                        }}
                                    >
                                        {emoji}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <PixelInput
                            type="email"
                            label="Email Address"
                            placeholder="traveler@dreamscape.io"
                            value={email}
                            onChange={setEmail}
                            name="email"
                            required
                        />

                        <PixelInput
                            type="password"
                            label="Password"
                            placeholder="••••••••"
                            value={password}
                            onChange={setPassword}
                            name="password"
                            required
                        />

                        <div className="pt-2">
                            <PixelButton
                                type="submit"
                                variant="primary"
                                fullWidth
                                disabled={isLoading}
                            >
                                {isLoading ? 'ENTERING...' : 'ENTER DREAMSCAPE'}
                            </PixelButton>
                        </div>
                    </form>

                    {/* Footer Links */}
                    <div className="mt-6 pt-6 border-t-4 border-dream-purple-700 text-center">
                        <p className="font-body text-sm text-dream-purple-400">
                            New to the dreamscape?
                        </p>
                        <Link
                            to="/signup"
                            className="font-pixel text-[9px] text-dream-yellow-500 hover:text-dream-yellow-300 transition-colors"
                        >
                            CREATE NEW PROFILE →
                        </Link>
                    </div>
                </PixelCard>

                {/* Decorative pixels */}
                <div className="flex justify-center mt-8 gap-2">
                    {[...Array(5)].map((_, i) => (
                        <div
                            key={i}
                            className="w-2 h-2 bg-dream-purple-600"
                            style={{
                                animation: 'pulse-soft 1.5s ease-in-out infinite',
                                animationDelay: `${i * 0.2}s`,
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
