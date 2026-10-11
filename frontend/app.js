// TonConnect UI ni ishga tushirish
const tonConnectUI = new TON_CONNECT_UI.TonConnectUI({
    manifestUrl: 'https://paxta.online/tonconnect-manifest.json', // Loyiha ishga tushganda haqiqiy URL ga almashtiriladi
    buttonRootId: 'ton-connect'
});

// Tab larni almashtirish mantiqi
function showTab(tabId) {
    // Barcha tab knopkalaridan 'active' klassini olib tashlash
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Barcha tab kontentlaridan 'active' klassini olib tashlash
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Tanlangan tab va kontentiga 'active' qo'shish
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }

    const targetBtn = document.querySelector(`button[onclick="showTab('${tabId}')"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
}

// Hamyon ulanganda ishlaydigan hodisa
tonConnectUI.onStatusChange(wallet => {
    if (wallet) {
        console.log('Hamyon ulandi:', wallet.account.address);
        // Bu yerda foydalanuvchi NFTlarini yuklash yoki boshqa mantiq yozilishi mumkin
    } else {
        console.log('Hamyon uzildi');
    }
});