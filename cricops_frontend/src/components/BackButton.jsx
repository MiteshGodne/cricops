export default function BackButton({ children, variant = 'primary', className = '', ...props }) {
    const base = 'bg-white text-center w-25 rounded-2xl h-10 relative text-black text-l font-semibold border-4 border-white group';
    return (
        <button type="button" className={`${base} ${className}`} {...props}>
            <div className="bg-[#efa800] rounded-lg h-8 w-1/3 grid place-items-center absolute text-center left-0 top-0 group-hover:w-full z-10 duration-500">
                <svg width="15px" height="15px" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                    <path fill="#000000" d="M224 480h640a32 32 0 1 1 0 64H224a32 32 0 0 1 0-64z" />
                    <path fill="#000000" d="m237.248 512 265.408 265.344a32 32 0 0 1-45.312 45.312l-288-288a32 32 0 0 1 0-45.312l288-288a32 32 0 1 1 45.312 45.312L237.248 512z" />
                </svg>
            </div>
            <p className="translate-x-2">{children}</p>
        </button>
    );
}
