/**
 * SignupPage Component
 * Retro registration form for new users
 * "Create your traveler profile" aesthetic
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PixelButton, PixelCard, PixelInput } from '../components/ui';
import { StarryBackground } from '../components/background';

interface SignupPageProps {
    onSignup?: () => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({ onSignup }) => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        setIsLoading(true);

        try {
            const { signup } = await import('../services/api');
            // Assuming name is used as extra metadata or we implement profile update later
            // The current api.signup only takes email/password, let's just pass that for now
            const result = await signup({ email, password, name });

            if (result.success) {
                // Auth state listener will handle redirect
                onSignup?.();
            } else {
                alert(result.error || 'Signup failed');
            }
        } catch (error) {
            console.error(error);
            alert('Signup error');
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
                        NEW TRAVELER
                    </h1>
                    <p className="font-pixel text-[10px] text-dream-yellow-500">
                        CREATE YOUR PROFILE
                    </p>
                </div>

                {/* Signup Form */}
                <PixelCard variant="dark">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Character creation header */}
                        <div className="text-center mb-4">
                            <div className="inline-block px-4 py-2 bg-dream-purple-700 border-4 border-dream-purple-500">
                                <span className="font-pixel text-[8px] text-dream-yellow-500">
                                    ⭐ CHARACTER CREATION ⭐
                                </span>
                            </div>
                        </div>

                        <PixelInput
                            type="text"
                            label="Traveler Name"
                            placeholder="Enter your name"
                            value={name}
                            onChange={setName}
                            name="name"
                            required
                        />

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
                            placeholder="Create a password"
                            value={password}
                            onChange={setPassword}
                            name="password"
                            required
                        />

                        <PixelInput
                            type="password"
                            label="Confirm Password"
                            placeholder="Confirm your password"
                            value={confirmPassword}
                            onChange={setConfirmPassword}
                            name="confirmPassword"
                            required
                        />

                        {/* Stats preview - just for fun */}
                        <div className="bg-dream-purple-800 border-4 border-dream-purple-600 p-3">
                            <p className="font-pixel text-[7px] text-dream-purple-300 text-center mb-2">
                                STARTING STATS
                            </p>
                            <div className="grid grid-cols-3 gap-2 text-center">
                                <div>
                                    <p className="font-pixel text-[10px] text-dream-yellow-500">99</p>
                                    <p className="font-body text-[10px] text-dream-purple-400">Sleep</p>
                                </div>
                                <div>
                                    <p className="font-pixel text-[10px] text-dream-yellow-500">99</p>
                                    <p className="font-body text-[10px] text-dream-purple-400">Dream</p>
                                </div>
                                <div>
                                    <p className="font-pixel text-[10px] text-dream-yellow-500">99</p>
                                    <p className="font-body text-[10px] text-dream-purple-400">Rest</p>
                                </div>
                            </div>
                        </div>

                        <div className="pt-2">
                            <PixelButton
                                type="submit"
                                variant="primary"
                                fullWidth
                                disabled={isLoading}
                            >
                                {isLoading ? 'CREATING...' : 'BEGIN ADVENTURE'}
                            </PixelButton>
                        </div>
                    </form>

                    {/* Footer Links */}
                    <div className="mt-6 pt-6 border-t-4 border-dream-purple-700 text-center">
                        <p className="font-body text-sm text-dream-purple-400">
                            Already a traveler?
                        </p>
                        <Link
                            to="/login"
                            className="font-pixel text-[9px] text-dream-yellow-500 hover:text-dream-yellow-300 transition-colors"
                        >
                            RETURN TO LOGIN →
                        </Link>
                    </div>
                </PixelCard>
            </div>
        </div>
    );
};

export default SignupPage;
