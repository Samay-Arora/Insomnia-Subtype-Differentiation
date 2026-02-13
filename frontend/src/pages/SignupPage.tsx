import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PixelButton, PixelCard, PixelInput } from '../components/ui';
import { StarryBackground } from '../components/background';
import { signup } from '../services/api';

export const SignupPage = ({ onSignup }: { onSignup?: () => void }) => {
    const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
    const [loading, setLoading] = useState(false);

    const update = (field: string) => (val: string) => {
        setForm(prev => ({ ...prev, [field]: val }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (form.password !== form.confirm) return alert('Passwords mismatch');

        setLoading(true);
        try {
            const res = await signup({
                email: form.email,
                password: form.password,
                name: form.name
            });

            if (res.success) onSignup?.();
            else alert(res.error || 'Signup failed');
        } catch (err) {
            console.error(err);
            alert('Error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-dream-indigo-900 via-dream-purple-900 to-dream-purple-800 relative flex items-center justify-center p-4">
            <StarryBackground starCount={40} />

            <div className="relative z-10 w-full max-w-md">
                <div className="text-center mb-8">
                    <Link to="/" className="inline-block mb-6">
                        <span className="font-pixel text-[10px] text-dream-purple-400 hover:text-dream-purple-300">
                            ← BACK
                        </span>
                    </Link>
                    <h1 className="font-pixel text-xl text-pixel-white mb-2">SIGN UP</h1>
                    <p className="font-pixel text-[10px] text-dream-yellow-500">CREATE PROFILE</p>
                </div>

                <PixelCard variant="dark">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <PixelInput
                            label="Name"
                            placeholder="Your name"
                            value={form.name}
                            onChange={update('name')}
                            required
                        />
                        <PixelInput
                            type="email"
                            label="Email"
                            placeholder="user@example.com"
                            value={form.email}
                            onChange={update('email')}
                            required
                        />
                        <PixelInput
                            type="password"
                            label="Password"
                            placeholder="******"
                            value={form.password}
                            onChange={update('password')}
                            required
                        />
                        <PixelInput
                            type="password"
                            label="Confirm"
                            placeholder="******"
                            value={form.confirm}
                            onChange={update('confirm')}
                            required
                        />

                        <div className="bg-dream-purple-800 border-4 border-dream-purple-600 p-3">
                            <p className="font-pixel text-[7px] text-dream-purple-300 text-center mb-2">INITIAL STATS</p>
                            <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
                                <div><p className="text-dream-yellow-500">99</p><p className="text-dream-purple-400">Sleep</p></div>
                                <div><p className="text-dream-yellow-500">99</p><p className="text-dream-purple-400">Dream</p></div>
                                <div><p className="text-dream-yellow-500">99</p><p className="text-dream-purple-400">Rest</p></div>
                            </div>
                        </div>

                        <div className="pt-2">
                            <PixelButton type="submit" variant="primary" fullWidth disabled={loading}>
                                {loading ? 'CREATING...' : 'BEGIN'}
                            </PixelButton>
                        </div>
                    </form>

                    <div className="mt-6 pt-6 border-t-4 border-dream-purple-700 text-center">
                        <Link to="/login" className="font-pixel text-[9px] text-dream-yellow-500 hover:text-dream-yellow-300">
                            LOGIN →
                        </Link>
                    </div>
                </PixelCard>
            </div>
        </div>
    );
};

export default SignupPage;
