REJECTION_REASONS_MAP = {
    "Fake_document": "Fake_document",
    "Not_Covered": "Not_Covered",
    "Policy_expired": "Policy_expired"
}

def preprocess_insurance_data(file_path):
    """
    Preprocesses insurance claim data without using external libraries.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries containing cleaned data
    """

    cleaned_data = []
    headers = []
    
    try:
        with open(file_path, 'r') as file:

            lines = file.readlines()
            # print(lines[0])
            
            if len(lines) == 0:
                print("Error: Empty file")
                return []
            

            headers = [header.strip() for header in lines[0].strip().split(',')]

            for i in range(1, len(lines)):
                line = lines[i].strip()
                if not line:  
                    continue
                    
                row = line.split(',')
               
                row_dict = {}
                
                for j in range(len(headers)):
                    if j < len(row):
                        row_dict[headers[j]] = row[j].strip() if row[j].strip() else None
                    else:
                        row_dict[headers[j]] = None
                
                
                # Clean and convert data types
                # CLAIM_ID: Validate claim ID format
                claim_id = row_dict.get('CLAIM_ID')
                if claim_id and claim_id.startswith('CLM'):
                    row_dict['CLAIM_ID'] = claim_id
                elif claim_id:
                    row_dict['CLAIM_ID'] = f"INVALID_{claim_id}"
                else:
                    row_dict['CLAIM_ID'] = "MISSING_CLAIM_ID"
                
                # CLAIM_DATE: date format checking (YYYY-MM-DD)
                claim_date = row_dict.get('CLAIM_DATE')
                if claim_date and len(claim_date.split('-')) == 3:
                    date_parts = claim_date.split('-')
                    try:
                        year = int(date_parts[0])
                        month = int(date_parts[1])
                        day = int(date_parts[2])
                        if 1900 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                            row_dict['CLAIM_DATE'] = claim_date
                        else:
                            row_dict['CLAIM_DATE'] = None
                    except ValueError:
                        row_dict['CLAIM_DATE'] = None
                else:
                    row_dict['CLAIM_DATE'] = None
                
                # CUSTOMER_ID: check is it a valid string
                customer_id = row_dict.get('CUSTOMER_ID')
                if customer_id and customer_id.startswith('CUST'):
                    row_dict['CUSTOMER_ID'] = customer_id
                elif customer_id:
                    row_dict['CUSTOMER_ID'] = f"INVALID_{customer_id}"
                else:
                    row_dict['CUSTOMER_ID'] = "MISSING_CUSTOMER_ID"
                
                # CLAIM_AMOUNT: Convert to float if possible
                claim_amount_str = row_dict.get('CLAIM_AMOUNT')
                try:
                    row_dict['CLAIM_AMOUNT'] = float(claim_amount_str) if claim_amount_str else 0.0
                except (ValueError, TypeError):
                    row_dict['CLAIM_AMOUNT'] = 0.0
                
                # PREMIUM_COLLECTED: Convert to float if possible
                premium_collected_str = row_dict.get('PREMIUM_COLLECTED')
                try:
                    row_dict['PREMIUM_COLLECTED'] = float(premium_collected_str) if premium_collected_str else 0.0
                except (ValueError, TypeError):
                    row_dict['PREMIUM_COLLECTED'] = 0.0
                
                # PAID_AMOUNT: Convert to float if possible
                paid_amount_str = row_dict.get('PAID_AMOUNT')
                try:
                    row_dict['PAID_AMOUNT'] = float(paid_amount_str) if paid_amount_str else 0.0
                except (ValueError, TypeError):
                    row_dict['PAID_AMOUNT'] = 0.0
                
                # CITY:  checking city names, taking default currently
                city = row_dict.get('CITY')
                valid_cities = ['PUNE', 'GUWAHATI', 'RANCHI', 'KOLKATA']
                if city and city.upper() in valid_cities:
                    row_dict['CITY'] = city.upper()
                else:
                    row_dict['CITY'] = 'UNKNOWN'
                
                # Add the cleaned row to our dataset
                cleaned_data.append(row_dict)
        
        print(f"Successfully processed {len(cleaned_data)} records")
        return cleaned_data
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []


def handle_error(error_message):
    print(f"Error: {error_message}")  
    return "Error"      


def contains_rejection_reason(rejection_text, reason):
    try:
        if rejection_text and isinstance(rejection_text, str):
            return reason.lower() in rejection_text.lower()  
    except Exception as e:  
        handle_error(f"Error in contains_rejection_reason: {str(e)}")
        return False
    return False


def map_rejection_reason(rejection_text):
    try:
        if rejection_text and isinstance(rejection_text, str):
            for reason, rejection_class in REJECTION_REASONS_MAP.items():  
                if contains_rejection_reason(rejection_text, reason):
                    return rejection_class
            return "Unknown"
        else:
            return "NoRemark"
    except Exception as e:
        handle_error(f"Error in map_rejection_reason: {str(e)}")
        return "Error"  


def complex_rejection_classifier(remark_text):
    try:
        if not isinstance(remark_text, str) or len(remark_text.strip()) == 0:  
            return "Invalid Remark"
        
        # Check for each rejection reason
        fake_doc = contains_rejection_reason(remark_text, "Fake_document")  
        not_covered = contains_rejection_reason(remark_text, "Not_Covered")
        policy_expired = contains_rejection_reason(remark_text, "Policy_expired")
        
        if fake_doc:
            return "Fake_document"  
        elif not_covered:
            return "Not_Covered"
        elif policy_expired:
            return "Policy_expired"
        else:
            # Unknown or null remarks
            return map_rejection_reason(remark_text)
    except Exception as e:
        handle_error(f"Error in complex_rejection_classifier: {str(e)}")
        return "Error"  


def analyze_city_performance(data):
    """
    Analyzes city performance to recommend which city to close based on profitability metrics.
    
    Args:
        data (list): List of dictionaries containing cleaned insurance data
    
    Returns:
        dict: Dictionary containing analysis results per city
    """
    # Initialize city metrics
    city_metrics = {
        'PUNE': {'claims': 0, 'claim_amount': 0, 'premium': 0, 'paid': 0, 'rejection_count': 0},
        'KOLKATA': {'claims': 0, 'claim_amount': 0, 'premium': 0, 'paid': 0, 'rejection_count': 0},
        'RANCHI': {'claims': 0, 'claim_amount': 0, 'premium': 0, 'paid': 0, 'rejection_count': 0},
        'GUWAHATI': {'claims': 0, 'claim_amount': 0, 'premium': 0, 'paid': 0, 'rejection_count': 0},
        'UNKNOWN': {'claims': 0, 'claim_amount': 0, 'premium': 0, 'paid': 0, 'rejection_count': 0}
    }
    
    # Calculate metrics for each city
    for row in data:
        city = row.get('CITY', 'UNKNOWN')
        if city not in city_metrics:
            city = 'UNKNOWN'
        
        # Increment claim count
        city_metrics[city]['claims'] += 1
        
        # Add claim amount
        claim_amount = row.get('CLAIM_AMOUNT', 0)
        city_metrics[city]['claim_amount'] += float(claim_amount) if isinstance(claim_amount, (int, float)) else 0
        
        # Add premium collected
        premium = row.get('PREMIUM_COLLECTED', 0)
        city_metrics[city]['premium'] += float(premium) if isinstance(premium, (int, float)) else 0
        
        # Add paid amount
        paid_amount = row.get('PAID_AMOUNT', 0)
        city_metrics[city]['paid'] += float(paid_amount) if isinstance(paid_amount, (int, float)) else 0
        
        # Check if claim was rejected (fixed comparison with 0.0)
        if float(paid_amount) == 0.0 and row.get('REJECTION_REMARKS'):
            city_metrics[city]['rejection_count'] += 1
    
    # Calculate profitability and other KPIs for each city
    city_results = {}
    
    for city, metrics in city_metrics.items():
        if city != 'UNKNOWN' and metrics['claims'] > 0:  # Only include cities with claims
            # Calculate profit (premium - paid)
            profit = metrics['premium'] - metrics['paid']
            
            # Calculate profit margin
            profit_margin = (profit / metrics['premium']) * 100 if metrics['premium'] > 0 else 0
            
            # Calculate claim rejection rate
            rejection_rate = (metrics['rejection_count'] / metrics['claims']) * 100 if metrics['claims'] > 0 else 0
            
            # Calculate average claim amount
            avg_claim = metrics['claim_amount'] / metrics['claims'] if metrics['claims'] > 0 else 0
            
            # Calculate average premium
            avg_premium = metrics['premium'] / metrics['claims'] if metrics['claims'] > 0 else 0
            
            # Store calculated metrics
            city_results[city] = {
                'claims': metrics['claims'],
                'total_claim_amount': metrics['claim_amount'],
                'total_premium': metrics['premium'],
                'total_paid': metrics['paid'],
                'profit': profit,
                'profit_margin': profit_margin,
                'rejection_rate': rejection_rate,
                'avg_claim': avg_claim,
                'avg_premium': avg_premium
            }
    
    return city_results


def recommend_city_closure(city_results):
    """
    Recommends which city to close based on various performance metrics.
    
    Args:
        city_results (dict): Dictionary containing analysis results per city
    
    Returns:
        tuple: (recommended_city, justification)
    """
    if not city_results:
        return (None, "No city data available for analysis")
    
    # Initialize variables for comparison
    min_profit_city = None
    min_profit = float('inf')
    
    min_margin_city = None
    min_margin = float('inf')
    
    # Compare cities based on profitability
    for city, metrics in city_results.items():
        # Check for lowest profit
        if metrics['profit'] < min_profit:
            min_profit = metrics['profit']
            min_profit_city = city
        
        # Check for lowest profit margin
        if metrics['profit_margin'] < min_margin:
            min_margin = metrics['profit_margin']
            min_margin_city = city
    
    # Create a weighted score for each city (lower is worse)
    city_scores = {}
    max_profit = max([c['profit'] for c in city_results.values()]) if city_results else 1
    max_margin = max([c['profit_margin'] for c in city_results.values()]) if city_results else 1
    
    for city, metrics in city_results.items():
        # Score based on multiple factors (profit, profit margin)
        # Normalize values to be between 0 and 1
        profit_score = metrics['profit'] / max_profit if max_profit > 0 else 0
        margin_score = metrics['profit_margin'] / max_margin if max_margin > 0 else 0
        
        # Weighted score (higher weight on profit and profit margin)
        city_scores[city] = (0.6 * profit_score) + (0.4 * margin_score)
    
    # Find city with lowest score
    recommended_closure = min(city_scores.items(), key=lambda x: x[1])[0]
    
    # Create justification
    justification = f"Based on the analysis, {recommended_closure} should be considered for closure due to:\n"
    justification += f"- Profit: ₹{city_results[recommended_closure]['profit']:.2f}\n"
    justification += f"- Profit Margin: {city_results[recommended_closure]['profit_margin']:.2f}%\n"
    justification += f"- Total Claims: {city_results[recommended_closure]['claims']}\n"
    justification += f"- Average Claim Amount: ₹{city_results[recommended_closure]['avg_claim']:.2f}\n"
    justification += f"- Rejection Rate: {city_results[recommended_closure]['rejection_rate']:.2f}%\n"
    
    return (recommended_closure, justification)


# Example usage
if __name__ == "__main__":
    # Process the data
    cleaned_data = preprocess_insurance_data("Insurance_auto_data.csv")
    
    if cleaned_data:
        # Apply the rejection classifier to add rejection classes
        for row in cleaned_data:
            if row.get('REJECTION_REMARKS'):
                row['REJECTION_CLASS'] = complex_rejection_classifier(row['REJECTION_REMARKS'])
            else:
                row['REJECTION_CLASS'] = 'No Remark'
        
        # Analyze city performance
        city_results = analyze_city_performance(cleaned_data)
        
        if city_results:
            # Display city performance summary
            print("\nCity Performance Summary:")
            print("-" * 80)
            for city, metrics in city_results.items():
                print(f"\n{city}:")
                print(f"  Claims: {metrics['claims']}")
                print(f"  Total Premium: ₹{metrics['total_premium']:.2f}")
                print(f"  Total Paid: ₹{metrics['total_paid']:.2f}")
                print(f"  Profit: ₹{metrics['profit']:.2f}")
                print(f"  Profit Margin: {metrics['profit_margin']:.2f}%")
                print(f"  Rejection Rate: {metrics['rejection_rate']:.2f}%")
            
            # Get recommendation for city closure
            recommended_city, justification = recommend_city_closure(city_results)
            
            print(f"\n{'='*50}")
            print(f"Recommended city for closure: {recommended_city}")
            print("=" * 50)
            print(justification)
        else:
            print("No valid city data found for analysis")
    else:
        print("No data could be processed from the file")