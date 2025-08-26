import React, { useState } from 'react';
// import brightKidsLogo from '../assets/bright-kids-logo-white.png';
import './RegistrationForm.css';

const RegistrationForm = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // بيانات الطفل
    childName: '',
    birthDate: '',
    age: '',
    gender: '',
    nationality: '',
    birthPlace: '',
    childPhoto: null,
    
    // بيانات ولي الأمر
    parentName: '',
    relationship: '',
    phoneNumber: '',
    emergencyPhone: '',
    email: '',
    address: '',
    
    // معلومات التغذية
    feedingCount: '',
    feedingTimes: '',
    milkType: '',
    milkBrand: '',
    breakfast: '',
    lunch: '',
    dinner: '',
    snacks: '',
    
    // الحالة الصحية
    hasAllergies: false,
    allergiesDetails: '',
    medications: '',
    emergencyInstructions: '',
    
    // خيارات الاشتراك
    transportService: false,
    mealService: false,
    
    // تفويض الاستلام
    authorizedPersons: [
      { name: '', relationship: '', phone: '' },
      { name: '', relationship: '', phone: '' },
      { name: '', relationship: '', phone: '' }
    ],
    
    // المستندات
    documents: {
      familyCard: null,
      childPhotos: null,
      birthCertificate: null,
      vaccinations: null,
      parentId: null
    }
  });

  const totalSteps = 8;

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAuthorizedPersonChange = (index, field, value) => {
    const updatedPersons = [...formData.authorizedPersons];
    updatedPersons[index][field] = value;
    setFormData(prev => ({
      ...prev,
      authorizedPersons: updatedPersons
    }));
  };

  const handleFileUpload = (field, file) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: file
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: file
      }));
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = () => {
    console.log('Form submitted:', formData);
    // هنا سيتم إرسال البيانات إلى الخادم
    alert('تم إرسال طلب التسجيل بنجاح!');
  };

  const renderProgressBar = () => (
    <div className="w-full bg-gray-200 rounded-full h-3 mb-8">
      <div 
        className="bg-gradient-to-r from-bright-orange to-bright-blue h-3 rounded-full progress-bar"
        style={{ width: `${(currentStep / totalSteps) * 100}%` }}
      ></div>
    </div>
  );

  const renderStep1 = () => (
    <div className="form-step">
      <h2 className="text-2xl font-bold text-bright-blue mb-6">بيانات الطفل</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            الاسم الكامل للطفل *
          </label>
          <input
            type="text"
            value={formData.childName}
            onChange={(e) => handleInputChange('childName', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="أدخل الاسم الكامل"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            تاريخ الميلاد *
          </label>
          <input
            type="date"
            value={formData.birthDate}
            onChange={(e) => handleInputChange('birthDate', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            العمر *
          </label>
          <input
            type="text"
            value={formData.age}
            onChange={(e) => handleInputChange('age', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="مثال: سنتان و 6 أشهر"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            الجنس *
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="gender"
                value="ذكر"
                checked={formData.gender === 'ذكر'}
                onChange={(e) => handleInputChange('gender', e.target.value)}
                className="ml-2"
              />
              ذكر
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="gender"
                value="أنثى"
                checked={formData.gender === 'أنثى'}
                onChange={(e) => handleInputChange('gender', e.target.value)}
                className="ml-2"
              />
              أنثى
            </label>
          </div>
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            الجنسية *
          </label>
          <input
            type="text"
            value={formData.nationality}
            onChange={(e) => handleInputChange('nationality', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="الجنسية"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            مكان الميلاد *
          </label>
          <input
            type="text"
            value={formData.birthPlace}
            onChange={(e) => handleInputChange('birthPlace', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="مكان الميلاد"
            required
          />
        </div>
      </div>

      <div className="mt-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          صورة الطفل *
        </label>
        <div className="file-upload-area border-2 border-dashed border-bright-blue rounded-lg p-6 text-center">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileUpload('childPhoto', e.target.files[0])}
            className="hidden"
            id="childPhoto"
          />
          <label htmlFor="childPhoto" className="cursor-pointer">
            <div className="text-bright-blue text-lg mb-2">📷</div>
            <p className="text-gray-600">اضغط لرفع صورة الطفل</p>
            {formData.childPhoto && (
              <p className="text-green-600 mt-2">تم رفع الصورة: {formData.childPhoto.name}</p>
            )}
          </label>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="form-step">
      <h2 className="text-2xl font-bold text-bright-blue mb-6">بيانات ولي الأمر</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            اسم ولي الأمر *
          </label>
          <input
            type="text"
            value={formData.parentName}
            onChange={(e) => handleInputChange('parentName', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="الاسم الكامل لولي الأمر"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            صلة القرابة *
          </label>
          <select
            value={formData.relationship}
            onChange={(e) => handleInputChange('relationship', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            required
          >
            <option value="">اختر صلة القرابة</option>
            <option value="الأب">الأب</option>
            <option value="الأم">الأم</option>
            <option value="الجد">الجد</option>
            <option value="الجدة">الجدة</option>
            <option value="العم">العم</option>
            <option value="العمة">العمة</option>
            <option value="الخال">الخال</option>
            <option value="الخالة">الخالة</option>
            <option value="أخرى">أخرى</option>
          </select>
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            رقم الجوال *
          </label>
          <input
            type="tel"
            value={formData.phoneNumber}
            onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="+966 53 750 6160"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            رقم آخر للطوارئ *
          </label>
          <input
            type="tel"
            value={formData.emergencyPhone}
            onChange={(e) => handleInputChange('emergencyPhone', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="رقم جوال آخر للطوارئ"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-bold mb-2">
            البريد الإلكتروني *
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="example@email.com"
            required
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            العنوان *
          </label>
          <textarea
            value={formData.address}
            onChange={(e) => handleInputChange('address', e.target.value)}
            className="input-field w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-bright-blue"
            placeholder="العنوان الكامل"
            rows="3"
            required
          />
        </div>
      </div>
    </div>
  );

  const renderNavigationButtons = () => (
    <div className="flex justify-between mt-8">
      <button
        onClick={prevStep}
        disabled={currentStep === 1}
        className={`px-6 py-3 rounded-lg font-semibold ${
          currentStep === 1
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'btn-secondary text-white hover:shadow-lg'
        }`}
      >
        السابق
      </button>

      {currentStep === totalSteps ? (
        <button
          onClick={handleSubmit}
          className="btn-primary text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg"
        >
          إرسال الطلب
        </button>
      ) : (
        <button
          onClick={nextStep}
          className="btn-primary text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg"
        >
          التالي
        </button>
      )}
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderStep1();
      case 2:
        return renderStep2();
      default:
        return renderStep1();
    }
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 h-24 w-24 bg-gradient-to-r from-bright-orange to-bright-blue rounded-full flex items-center justify-center">
            <span className="text-white text-2xl font-bold">BK</span>
          </div>
          <h1 className="text-3xl font-bold text-bright-blue mb-2">
            استمارة تسجيل طفل جديد
          </h1>
          <p className="text-gray-600">
            مركز Bright Kids للحضانة - YADC7069
          </p>
          <p className="text-gray-600">
            حي قرطبة، 46429، ينبع | +966 53 750 6160
          </p>
        </div>

        {/* Progress Bar */}
        {renderProgressBar()}

        {/* Step Indicator */}
        <div className="flex justify-center mb-8">
          <div className="text-center">
            <span className="text-lg font-semibold text-bright-blue">
              الخطوة {currentStep} من {totalSteps}
            </span>
          </div>
        </div>

        {/* Form Content */}
        <div className="card rounded-xl shadow-xl p-8 mb-8">
          {renderCurrentStep()}
          {renderNavigationButtons()}
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm">
          <p>جميع الحقول المميزة بـ (*) مطلوبة</p>
          <p className="mt-2">
            للمساعدة: +966 53 750 6160 | 
            <a 
              href="https://www.google.com/maps/dir/?api=1&destination=24.0857962992111%2C38.0875255905884"
              target="_blank"
              rel="noopener noreferrer"
              className="text-bright-blue hover:underline mr-2"
            >
              الموقع على الخريطة
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegistrationForm;

