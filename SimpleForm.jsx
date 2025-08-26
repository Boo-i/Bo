import React, { useState } from 'react';

const SimpleForm = () => {
  const [formData, setFormData] = useState({
    childName: '',
    parentName: '',
    phone: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('تم إرسال النموذج بنجاح!');
    console.log(formData);
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif',
      direction: 'rtl'
    }}>
      <div style={{ 
        maxWidth: '600px', 
        margin: '0 auto',
        background: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #FF6B35 0%, #4A90E2 100%)',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '24px',
            fontWeight: 'bold'
          }}>
            BK
          </div>
          <h1 style={{ 
            color: '#4A90E2', 
            fontSize: '2rem', 
            marginBottom: '0.5rem',
            fontWeight: 'bold'
          }}>
            استمارة تسجيل طفل جديد
          </h1>
          <p style={{ color: '#666', margin: '0.25rem 0' }}>
            مركز Bright Kids للحضانة - YADC7069
          </p>
          <p style={{ color: '#666', margin: '0.25rem 0' }}>
            حي قرطبة، 46429، ينبع | +966 53 750 6160
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 'bold',
              color: '#333'
            }}>
              اسم الطفل *
            </label>
            <input
              type="text"
              name="childName"
              value={formData.childName}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '1rem',
                transition: 'border-color 0.3s ease'
              }}
              placeholder="أدخل اسم الطفل"
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 'bold',
              color: '#333'
            }}>
              اسم ولي الأمر *
            </label>
            <input
              type="text"
              name="parentName"
              value={formData.parentName}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '1rem',
                transition: 'border-color 0.3s ease'
              }}
              placeholder="أدخل اسم ولي الأمر"
            />
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 'bold',
              color: '#333'
            }}>
              رقم الهاتف *
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '1rem',
                transition: 'border-color 0.3s ease'
              }}
              placeholder="+966 53 750 6160"
            />
          </div>

          <button
            type="submit"
            style={{
              width: '100%',
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 25px rgba(255, 107, 53, 0.3)';
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            إرسال الطلب
          </button>
        </form>

        {/* Footer */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '2rem', 
          color: '#666',
          fontSize: '0.9rem'
        }}>
          <p>جميع الحقول المميزة بـ (*) مطلوبة</p>
          <p style={{ marginTop: '0.5rem' }}>
            للمساعدة: +966 53 750 6160 | 
            <a 
              href="https://www.google.com/maps/dir/?api=1&destination=24.0857962992111%2C38.0875255905884"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#4A90E2', textDecoration: 'none', marginRight: '0.5rem' }}
            >
              الموقع على الخريطة
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleForm;

