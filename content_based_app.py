import streamlit as st
import pandas as pd
import pickle
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="📘 Slide Recommender System", layout="wide")
st.title("👩‍💻 Trình bày Đồ án Recommender System - Nhóm Tuấn - Tấn")

# Đường dẫn đến file PDF
#pdf_file_path = "Slide_Pro2_Recommend.pdf"

st.markdown(
    """
    <iframe src="https://docs.google.com/presentation/d/1BzLwaipvLELod0I-ePzcYPEsRPwS23ae/embed?start=false&loop=false&delayms=5000"
    frameborder="0" width="100%" height="600" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
    """,
    unsafe_allow_html=True
)

with open('products_cosine_sim.pkl', 'rb') as f:
    cosine_sim_new = pickle.load(f)
# function cần thiết
def get_recommendations(df, ma_san_pham, cosine_sim=cosine_sim_new, nums=5):
    # Get the index of the product that matches the ma_san_pham
    # and ensure it is within the bounds of the cosine_sim matrix
    matching_indices = df.index[df['product_id'] == ma_san_pham].tolist()
    if not matching_indices:
        print(f"No product found with ID: {ma_san_pham}")
        return pd.DataFrame()  # Return an empty DataFrame if no match
    idx = matching_indices[0]
    idx = min(idx, cosine_sim.shape[0] - 1)  # Limit idx to the maximum row index

    # Get the pairwise similarity scores of all products with the target product
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the products based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the top similar products (ignoring the product itself)
    sim_scores = sim_scores[1:nums + 1]

    # Get the product indices
    product_indices = [i[0] for i in sim_scores]

    # Return the top similar products as a DataFrame
    return df.iloc[product_indices]

# Hiển thị đề xuất ra bảng
def display_recommended_products(recommended_products, cols=5):
    for i in range(0, len(recommended_products), cols):
        cols = st.columns(cols)
        for j, col in enumerate(cols):
            if i + j < len(recommended_products):
                product = recommended_products.iloc[i + j]
                with col:   
                    st.write(product['product_name'])                    
                    expander = st.expander(f"Mô tả")
                    product_description = product['description_clean']
                    truncated_description = ' '.join(product_description.split()[:100]) + '...'
                    expander.write(truncated_description)
                    expander.markdown("Nhấn vào mũi tên để đóng hộp text này.")           
# Đọc dữ liệu sản phẩm
df_products = pd.read_csv('San_pham_temp.csv')
# Lấy 10 sản phẩm
random_products = df_products.head(n=10)
# print(random_products)

st.session_state.random_products = random_products

# Open and read file to cosine_sim_new

#---------------------------------
###### Giao diện Streamlit ######
#---------------------------------
#st.image('hasaki_banner.jpg', use_column_width=True)
# use_container_width 


# Cấu hình giao diện


# Đọc và mã hóa file PDF
# with open(pdf_file_path, "rb") as f:
#     base64_pdf = base64.b64encode(f.read()).decode("utf-8")

# Nhúng file PDF vào giao diện qua iframe
# pdf_viewer = f"""
# <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900px" type="application/pdf"></iframe>
# """
# st.image('shopee.jpeg', use_container_width =True)


# st.markdown(pdf_viewer, unsafe_allow_html=True)



# Kiểm tra xem 'selected_ma_san_pham' đã có trong session_state hay chưa
st.markdown(
    """
    <h2 style='text-align: center; color: #e91e63; font-size: 30px; font-weight: bold;'>
       ======================================================
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h2 style='text-align: center; color: #e91e63; font-size: 30px; font-weight: bold;'>
        🚀 Danh sách bạn có thể lựa chọn
    </h2>
    """,
    unsafe_allow_html=True
)
if 'selected_ma_san_pham' not in st.session_state:
    # Nếu chưa có, thiết lập giá trị mặc định là None hoặc ID sản phẩm đầu tiên
    st.session_state.selected_ma_san_pham = None

product_options = [(row['product_name'], row['product_id']) for index, row in st.session_state.random_products.iterrows()]
st.session_state.random_products
# Tạo một dropdown với options là các tuple này
selected_product = st.selectbox(
    "Chọn sản phẩm",
    options=product_options,
    format_func=lambda x: x[0]  # Hiển thị tên sản phẩm
)
# Display the selected product
st.write("Bạn đã chọn:", selected_product)

# Cập nhật session_state dựa trên lựa chọn hiện tại
st.session_state.selected_ma_san_pham = selected_product[1]

if st.session_state.selected_ma_san_pham:
    st.write("ma_san_pham: ", st.session_state.selected_ma_san_pham)
    # Hiển thị thông tin sản phẩm được chọn
    selected_product = df_products[df_products['product_id'] == st.session_state.selected_ma_san_pham]

    if not selected_product.empty:
        st.write('#### Bạn vừa chọn:')
        st.write('### ', selected_product['product_name'].values[0])

        product_description = selected_product['description_clean'].values[0]
        truncated_description = ' '.join(product_description.split()[:100])
        st.write('##### Thông tin:')
        st.write(truncated_description, '...')

        st.write('##### Các sản phẩm liên quan:')
        recommendations = get_recommendations(df_products, st.session_state.selected_ma_san_pham, cosine_sim=cosine_sim_new, nums=3) 
        display_recommended_products(recommendations, cols=3)
    else:
        st.write(f"Không tìm thấy sản phẩm với ID: {st.session_state.selected_ma_san_pham}")
