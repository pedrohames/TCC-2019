# Wireless router end-to-end test automation
This project was developed during my graduation as my final work degree.
It is responsible for automating an end-to-end test on a wireless router. The test itself checks if the configuration of the channel setup using a config API is applied on the physical layer of the router.

## Steps as the test

- Set up the environment and configure the router with the channel to be tested.
- Wait for the environment to be able to be tested after applying the config.
- Start generating traffic through the DUT (Device Under Test).
- Capture the data using an SDR device.
- Some signal processing to check whether the spectrum mask limit is according to the requirements.
- Generate evidence of the test just performed.

## Abstract

During the last few years, the need for online devices, like smartphones, smart-TVs, and surveillance cameras, has grown and continues to grow. Considering this, many manufacturers chose for Wi-Fi technology to wirelessly connect their products. As a consequence of increasing Wi-Ficonnectivity, vendors of IEEE 802.11 standard access points and routers, are looking for ways to reduce the development time of these devices to meet market needs as soon as possible. Much of this time is spent on the extensive testing routines performed with these equipments, aiming to guarantee good performance, robustness, and reliability. In order to reduce the time invested in the validation, this final paper proposes an SDR-based system to automate part of the physical layer tests in the Intelbras ZEUS products. The system aims to perform test routines in all or a portion of the operating channels and bandwidths of these equipments, in order to verify if the spectral occupation is in accordance with its specification defined by IEEE. In the end, as a result of automation, the time invested in performing the tests is reduced, the reliability is increased and a report is automatically issued with the results obtained.
