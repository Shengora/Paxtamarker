import "@stdlib/deploy";

// TON dagi TEP-62 NFT standartiga ko'ra transfer xabari
message(0x5fcc3d14) Transfer {
    query_id: Int as uint64;
    new_owner: Address;
    response_destination: Address?;
    custom_payload: Cell?;
    forward_amount: Int as coins;
    forward_payload: Slice?;
}

// OwnershipAssigned xabari (NFT ni olganda marketga keladi)
message(0x05138d91) OwnershipAssigned {
    query_id: Int as uint64;
    prev_owner: Address;
    forward_payload: Slice; // bu yerda narx yoki boshqa ma'lumotlar bo'lishi mumkin
}

message SellNft {
    nft_address: Address;
    price: Int as coins;
}

message WithdrawNft {
    nft_address: Address;
}

message BuyNft {
    nft_address: Address;
}

message SetPrice {
    nft_address: Address;
    price: Int as coins;
}

struct MarketItem {
    nft_address: Address;
    owner: Address;
    price: Int as coins;
    is_for_sale: Bool;
}

contract NftMarketplace with Deployable {
    owner: Address;

    // Nft address -> MarketItem
    items: map<Address, MarketItem>;

    init() {
        self.owner = sender();
    }

    // NFT qabul qilish
    receive(msg: OwnershipAssigned) {
        let ctx: Context = context();
        let nft_address: Address = ctx.sender;
        let prev_owner: Address = msg.prev_owner;

        let item: MarketItem? = self.items.get(nft_address);

        if (item == null) {
            // Yangi depozit, sotuvda emas
            self.items.set(nft_address, MarketItem{
                nft_address: nft_address,
                owner: prev_owner,
                price: 0,
                is_for_sale: false
            });
        }
    }

    // NFT narxini belgilash va sotuvga qo'yish
    receive(msg: SetPrice) {
        let ctx: Context = context();
        let item: MarketItem? = self.items.get(msg.nft_address);

        require(item != null, "NFT not deposited in market");
        let n: MarketItem = item!!;
        require(n.owner == ctx.sender, "Only owner can set price");
        require(msg.price > 0, "Price must be greater than 0");

        self.items.set(msg.nft_address, MarketItem{
            nft_address: n.nft_address,
            owner: n.owner,
            price: msg.price,
            is_for_sale: true
        });
    }

    // NFT xarid qilish
    receive(msg: BuyNft) {
        let ctx: Context = context();
        let item: MarketItem? = self.items.get(msg.nft_address);

        require(item != null, "NFT not found in market");
        let n: MarketItem = item!!;
        require(n.is_for_sale, "NFT is not for sale");

        // Komissiya, masalan 0.05 TON transfer uchun
        let transfer_fee: Int = ton("0.05");
        let required_value: Int = n.price + transfer_fee;
        require(ctx.value >= required_value, "Insufficient funds including transfer fee");

        let previous_owner: Address = n.owner;

        // NFT ni yangi egasiga jo'natish
        send(SendParameters{
            to: n.nft_address,
            value: transfer_fee,
            bounce: true,
            mode: SendIgnoreErrors,
            body: Transfer{
                query_id: 0,
                new_owner: ctx.sender,
                response_destination: ctx.sender,
                custom_payload: null,
                forward_amount: 0,
                forward_payload: null
            }.toCell()
        });

        // Market holatini yangilash yoki o'chirish (agar faqat marketplace funksiyasi bo'lsa)
        self.items.set(msg.nft_address, null);

        // Eski egasiga pulni jo'natish
        send(SendParameters{
            to: previous_owner,
            bounce: true,
            value: n.price,
            mode: SendIgnoreErrors
        });

        // Ortiqcha pulni (change) jo'natish, bu butun qolgan mablag'ni qaytarishni anglatadi (mode: SendRemainingValue)
        send(SendParameters{
            to: ctx.sender,
            bounce: true,
            value: 0,
            mode: SendRemainingValue + SendIgnoreErrors
        });
    }

    // NFT ni yechib olish
    receive(msg: WithdrawNft) {
        let ctx: Context = context();
        let item: MarketItem? = self.items.get(msg.nft_address);

        require(item != null, "NFT not found");
        let n: MarketItem = item!!;
        require(n.owner == ctx.sender, "Not the owner");

        let transfer_fee: Int = ton("0.05");
        require(ctx.value >= transfer_fee, "Insufficient funds to cover transfer fee");

        // NFT ni qaytarib jo'natish
        send(SendParameters{
            to: n.nft_address,
            value: transfer_fee,
            bounce: true,
            mode: SendIgnoreErrors,
            body: Transfer{
                query_id: 0,
                new_owner: ctx.sender,
                response_destination: ctx.sender,
                custom_payload: null,
                forward_amount: 0,
                forward_payload: null
            }.toCell()
        });

        self.items.set(msg.nft_address, null);
    }

    get fun get_nft_status(nft_address: Address): MarketItem? {
        return self.items.get(nft_address);
    }
}