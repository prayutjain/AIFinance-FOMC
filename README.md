# AI Finance - FOMC Project

Our project focuses on the significant impact of Federal Open Market Committee (FOMC) statement releases on asset prices, including SPY, Treasury 1yr-3yr, and Euro-dollar. We observe high volatility on these release days, especially during the 2:30 press conference in Powell's era. Our aim is to develop a proof of concept (POC) that predicts textual data prior to the official release and forecasts the expected volatility in asset prices.

## Dataset
We make use of the following datasets in our research:
* Macro-economic indicators
* FOMC statements
* Press conference transcripts
* Macro-economic consensus data
* 1-minute interval asset prices data

## Research Methodology
Our research involves:
1. Implementing a Neural Network
2. Applying Language Model (LLM) to convert text to signal
3. Using LLM for question-answering based on context

## POC Explanation
We establish the volatility amplitude at or after 2:00 pm as H1, and at or after 2:30 pm as H2. 

For H1:
* Base Model: We use Macro indicators to predict H1, resulting in an efficiency score of X1.
* By adding LLM-generated FOMC statements to Macro indicators for predicting H1, we attain an efficiency of X2.
* Using actual Statements along with Macro indicators for predicting H1 gives us an efficiency of X3.

Our goal is to ensure that X1 < X2 <= X3.  

For H2:
* We use FOMC statements and realized values of indicators to predict H2, resulting in an efficiency score of Z1.
* By adding LLM-generated Q&A to FOMC statements and realized values of indicators, we get an efficiency of Z2.
* The efficiency score Z3 is obtained by using FOMC statements, realized values of indicators, and actual Q&A to predict H2.

Our target is to ensure that Z1 < Z2 <= Z3. If Z2 is slightly larger than Z1, then our POC has potential.
