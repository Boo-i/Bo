import React, { useState, useEffect } from 'react';

const RegistrationRequests = () => {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [selectedRegistration, setSelectedRegistration] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchRegistrations();
    fetchStats();
  }, []);

  const fetchRegistrations = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/registration/list');
      const data = await response.json();
      if (data.success) {
        setRegistrations(data.registrations);
      }
    } catch (error) {
      console.error('خطأ في جلب طلبات التسجيل:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/registration/stats');
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('خطأ في جلب الإحصائيات:', error);
    }
  };

  const updateRegistrationStatus = async (registrationNumber, newStatus, notes = '') => {
    try {
      const response = await fetch(`http://localhost:5000/api/registration/${registrationNumber}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          notes: notes
        })
      });
      
      const data = await response.json();
      if (data.success) {
        fetchRegistrations();
        fetchStats();
        setShowModal(false);
        alert('تم تحديث حالة الطلب بنجاح');
      } else {
        alert('حدث خطأ في تحديث الحالة');
      }
    } catch (error) {
      console.error('خطأ في تحديث الحالة:', error);
      alert('حدث خطأ في تحديث الحالة');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'pending_review': { label: 'قيد المراجعة', color: 'bg-yellow-100 text-yellow-800' },
      'approved': { label: 'مقبول', color: 'bg-green-100 text-green-800' },
      'rejected': { label: 'مرفوض', color: 'bg-red-100 text-red-800' },
      'contacted': { label: 'تم التواصل', color: 'bg-blue-100 text-blue-800' }
    };
    
    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-800' };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* إحصائيات سريعة */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">📋</span>
              </div>
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">إجمالي الطلبات</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-bold">⏳</span>
              </div>
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">قيد المراجعة</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✅</span>
              </div>
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">مقبولة</p>
              <p className="text-2xl font-bold text-gray-900">{stats.approved || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-orange-600 font-bold">📅</span>
              </div>
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">اليوم</p>
              <p className="text-2xl font-bold text-gray-900">{stats.today || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* قائمة طلبات التسجيل */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">طلبات التسجيل الجديدة</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  رقم الطلب
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  اسم الطفل
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ولي الأمر
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  رقم الجوال
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  تاريخ التقديم
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  الحالة
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {registrations.map((registration) => (
                <tr key={registration.registration_number} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {registration.registration_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {registration.child_data?.name || 'غير محدد'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {registration.parent_data?.name || 'غير محدد'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {registration.parent_data?.phone || 'غير محدد'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(registration.submission_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(registration.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedRegistration(registration);
                        setShowModal(true);
                      }}
                      className="text-blue-600 hover:text-blue-900 ml-4"
                    >
                      عرض التفاصيل
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {registrations.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-500">
                <p className="text-lg font-medium">لا توجد طلبات تسجيل</p>
                <p className="text-sm">سيتم عرض طلبات التسجيل الجديدة هنا</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* نافذة تفاصيل الطلب */}
      {showModal && selectedRegistration && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  تفاصيل طلب التسجيل - {selectedRegistration.registration_number}
                </h3>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-6">
                {/* بيانات الطفل */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">بيانات الطفل</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">الاسم</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.child_data?.name}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">تاريخ الميلاد</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.child_data?.birth_date}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">العمر</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.child_data?.age}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">الجنس</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.child_data?.gender}</p>
                    </div>
                  </div>
                </div>

                {/* بيانات ولي الأمر */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">بيانات ولي الأمر</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">الاسم</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.parent_data?.name}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">صلة القرابة</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.parent_data?.relationship}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">رقم الجوال</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.parent_data?.phone}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">البريد الإلكتروني</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.parent_data?.email}</p>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700">العنوان</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedRegistration.parent_data?.address}</p>
                    </div>
                  </div>
                </div>

                {/* الإجراءات */}
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button
                    onClick={() => updateRegistrationStatus(selectedRegistration.registration_number, 'rejected')}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    رفض
                  </button>
                  <button
                    onClick={() => updateRegistrationStatus(selectedRegistration.registration_number, 'contacted')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    تم التواصل
                  </button>
                  <button
                    onClick={() => updateRegistrationStatus(selectedRegistration.registration_number, 'approved')}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    قبول
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RegistrationRequests;

