/**
 * LandingPage Component
 * Hero section with pixel-art moon, stars, and "ENTER THE DREAMSCAPE" title
 * Entry point for the Sleep Research Platform
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { PixelButton } from '../components/ui';
import { StarryBackground, PixelMoon, PixelCloud } from '../components/background';

export const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-gradient-to-b from-dream-indigo-900 via-dream-purple-900 to-dream-purple-800 relative overflow-hidden">
            {/* Starry Background */}
            <StarryBackground starCount={100} />

            {/* Floating Clouds */}
            <PixelCloud
                variant="lg"
                className="absolute top-20 left-10 animate-[float_8s_ease-in-out_infinite]"
                opacity={0.1}
            />
            <PixelCloud
                variant="md"
                className="absolute top-40 right-20 animate-[float_10s_ease-in-out_infinite]"
                opacity={0.08}
            />

            {/* Main Content */}
            <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
                {/* Moon */}
                <div className="mb-6">
                    <PixelMoon size="xl" animate />
                </div>

                {/* Pixel Art Sword / Knight Element */}
                <div className="mb-4 text-dream-yellow-500 font-pixel text-xs tracking-widest leading-none text-center">
                    <pre className="inline-block text-left">
{`      /| ________________
O|===|* >________________>
      \\|`}
                    </pre>
                </div>

                {/* Title */}
                <h1 className="font-pixel text-3xl md:text-4xl lg:text-5xl text-pixel-white text-center leading-relaxed mb-4 drop-shadow-lg">
                    NIGHT<span className="text-dream-yellow-500">KNIGHT</span>
                </h1>

                {/* Subtitle */}
                <p className="font-pixel text-[10px] md:text-xs text-dream-yellow-300 text-center max-w-2xl mb-8 leading-relaxed uppercase tracking-widest">
                    Your Quest Through The Dreamscape Begins
                </p>

                {/* Description */}
                <div className="max-w-xl text-center mb-10 pixel-border bg-dream-indigo-900/80 p-6">
                    <p className="font-body text-sm text-dream-purple-200 leading-relaxed">
                        The realm of sleep is plagued by mysterious disturbances. Equip your EEG data and embark on a journey. Our clinical algorithms will identify your unique insomnia subtype, helping researchers defeat the sleep demons.
                    </p>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4">
                    <Link to="/login">
                        <PixelButton variant="primary" size="lg">
                            Begin Quest
                        </PixelButton>
                    </Link>
                    <Link to="/signup">
                        <PixelButton variant="default" size="lg">
                            Join The Guild
                        </PixelButton>
                    </Link>
                    <PixelButton 
                        variant="ghost" 
                        size="lg" 
                        onClick={() => {
                            localStorage.setItem('offline_mode', 'true');
                            window.location.href = '/dashboard';
                        }}
                    >
                        Enter as Lone Wanderer
                    </PixelButton>
                </div>

                {/* Decorative pixel line */}
                <div className="mt-16 flex items-center gap-2">
                    {[...Array(7)].map((_, i) => (
                        <div
                            key={i}
                            className={`w-3 h-3 ${i === 3 ? 'bg-dream-yellow-500 w-4 h-4' : 'bg-dream-purple-500'}`}
                            style={{
                                animation: 'pulse-soft 2s ease-in-out infinite',
                                animationDelay: `${i * 0.15}s`,
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Bottom fade */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-dream-purple-800 to-transparent pointer-events-none" />
        </div>
    );
};

export default LandingPage;
