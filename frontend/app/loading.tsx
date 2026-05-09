"use client";

import { motion } from "framer-motion";

export default function Loading() {
  // ---- Animation Variants ----
  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.5 } }
  };

  const pulseVariants = {
    animate: {
      opacity: [0.3, 0.6, 0.3],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  const dotVariants = {
    animate: {
      scale: [1, 1.5, 1],
      opacity: [0.3, 1, 0.3],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="min-h-screen w-full flex items-center justify-center bg-zinc-950 antialiased overflow-hidden"
    >
      {/* Background Decorative Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="relative flex flex-col items-center gap-18">
        
        {/* Main Loading Visual */}
        <div className="relative flex items-center justify-center scale-110">
          
          {/* HIGH VISIBILITY Outer Pulsing Ring */}
          <motion.div 
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.15, 0.55, 0.15]
            }}
            transition={{ 
              duration: 2.5, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
            // Increased border thickness to 3px and added a strong neon glow
            className="absolute w-32 h-32 rounded-full border-[3px] border-blue-500/60 shadow-[0_0_30px_rgba(59,130,246,0.3)]"
          />
          
          {/* Rotating Spinner */}
          <div className="relative">
            <div className="h-16 w-16 rounded-full border-t-2 border-r-2 border-blue-500 animate-spin" />
            <div className="absolute inset-0 h-16 w-16 rounded-full border-2 border-zinc-900/50" />
          </div>

          {/* Center Core */}
          <div className="absolute h-2.5 w-2.5 bg-blue-500 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.9)]" />
        </div>

        {/* Text Interface */}
        <div className="flex flex-col items-center gap-3 text-center">
          <motion.h2 
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-zinc-100 font-semibold tracking-tight text-3xl"
          >
            Exam<span className="text-blue-500">AI</span>
          </motion.h2>
          
          <div className="flex items-center gap-2.5">
            <motion.span 
              variants={pulseVariants}
              animate="animate"
              className="text-zinc-500 text-sm font-mono tracking-[0.4em] uppercase"
            >
              Loading
            </motion.span>

            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  variants={dotVariants}
                  animate="animate"
                  transition={{ 
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.2 
                  }}
                  className="w-1 h-1 bg-blue-500 rounded-full shadow-[0_0_5px_rgba(59,130,246,0.4)]"
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .antialiased {
          background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1.5px, transparent 0);
          background-size: 50px 50px;
        }
      `}</style>
    </motion.div>
  );
}