import React from 'react';

function TestComponent() {
  const testData = [
    { id: 1, name: 'Test 1', status: 'active' },
    { id: 2, name: 'Test 2', status: 'paused' },
    { id: 3, name: 'Test 3', status: 'draft' }
  ];

  const handleClick = (id) => {
    console.log('Clicked:', id);
  };

  return (
    <div>
      <h1>Test Component</h1>
      <table>
        <tbody>
          {testData.map((item) => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{item.status}</td>
              <td>
                <button onClick={() => handleClick(item.id)}>
                  Click Me
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TestComponent;