import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Componente cronômetro que calcula e exibe a duração em tempo real
 * 
 * @param {Date} startTime - Data de início da chamada
 * @returns {JSX.Element} Componente JSX
 */
const Timer = ({ startTime }) => {
  const [duration, setDuration] = useState('00:00:00');
  
  useEffect(() => {
    if (!startTime) {
      setDuration('00:00:00');
      return;
    }
    
    // Converte a string da data para objeto Date
    const startDate = new Date(startTime);
    
    // Atualiza o cronômetro a cada segundo
    const intervalId = setInterval(() => {
      const now = new Date();
      const diffInSeconds = Math.floor((now - startDate) / 1000);
      
      // Formata o tempo como HH:MM:SS
      const hours = Math.floor(diffInSeconds / 3600);
      const minutes = Math.floor((diffInSeconds % 3600) / 60);
      const seconds = diffInSeconds % 60;
      
      const formattedTime = [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        seconds.toString().padStart(2, '0')
      ].join(':');
      
      setDuration(formattedTime);
    }, 1000);
    
    // Limpa o intervalo quando o componente é desmontado
    return () => clearInterval(intervalId);
  }, [startTime]);
  
  return (
    <span className="font-mono text-yellow-400 font-semibold">{duration}</span>
  );
};

Timer.propTypes = {
  startTime: PropTypes.string.isRequired
};

export default Timer; 