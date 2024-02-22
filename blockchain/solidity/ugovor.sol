pragma solidity ^0.8.2;

contract PaymentContract {
    address payable private owner;
    address payable private customer;
    address payable private courier;
    uint private value;
    bool private courier_set;

    constructor(address payable _customer) {
        owner = payable(msg.sender);
        customer = _customer;
        value = 0;
        courier_set = false;
    }

    function getOwner() public view returns (address payable) {
        return owner;
    }

    function getCustomer() public view returns (address payable) {
        return customer;
    }

    function getCourier() public view returns (address payable) {
        return courier;
    }

    function getCourierSet() public view returns (bool) {
        return courier_set;
    }

    function getValue() public view returns (uint) {
        return value;
    }

    function setOwner(address payable _owner) public {
        owner = _owner;
    }

    function setCustomer(address payable _customer) public {
        customer = _customer;
    }

    function setCourier(address payable _courier) public payable {
        courier = _courier;
        courier_set = true;
    }

    function setValue(uint _value) public {
        value = _value;
    }

    function sendMoney() public payable {
        require(msg.sender == customer, "Only customer can send money.");
        value += msg.value;
    }

    function payout() public payable {
        require(value > 0, "No funds available.");
        uint ownerAmount = (uint )((value * 80) / 100);
        uint courierAmount = (uint )((value * 20) / 100);
        value = 0;
        payable(owner).transfer(ownerAmount);
        payable(courier).transfer(courierAmount);
    }
}