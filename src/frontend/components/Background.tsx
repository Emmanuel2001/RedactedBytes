"use client";

export default function Background() {
  return (
    <div
      className="
        fixed inset-0 -z-10 
        transition-colors duration-200 backdrop-blur-sm
        bg-white dark:bg-neutral-800
      "
    />
  );
}