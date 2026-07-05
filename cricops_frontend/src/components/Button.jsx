import styled from 'styled-components';
export default function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'px-4 py-2 rounded text-sm font-medium transition disabled:opacity-50';
  // const variants = {
  //   primary: 'bg-blue-600 text-white hover:bg-blue-700',
  //   secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  //   danger: 'bg-red-600 text-white hover:bg-red-700',
  // };
  return (
    <StyledWrapper className='flex justify-center items-center'>
      <button className={`${base}  ${className} flex items-center`} {...props}>
        <span>{children}</span>
      </button>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
  button {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    background: #1b3a65;
    font-family: "Montserrat", sans-serif;
    box-shadow: 0px 6px 24px 0px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    cursor: pointer;
    border: none;
    height: 32px;
  }

  button:after {
    align-tems: center;
    content: " ";
    width: 0%;
    height: 100%;
    background: #efa800;
    // background: #ffd401;
    position: absolute;
    transition: all 0.4s ease-in-out;
    right: 0;
  }

  button:hover::after {
    right: auto;
    left: 0;
    width: 100%;
  }

  button span {
    text-align: center;
    align-items: center;
    text-decoration: none;
    width: 100%;
    color: #fff;
    font-size: 0.8em;
    font-weight: 700;
    letter-spacing: 0.1em;
    z-index: 10;
    transition: all 0.3s ease-in-out;
  }

  button:hover span {
    color: #1b3a65;
    animation: scaleUp 0.3s ease-in-out;
  }

  @keyframes scaleUp {
    0% {
      transform: scale(1);
    }

    50% {
      transform: scale(0.95);
    }

    100% {
      transform: scale(1);
    }
  }`;


