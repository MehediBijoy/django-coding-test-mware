import React, { useEffect, useState } from 'react'
import TagsInput from 'react-tagsinput'
import 'react-tagsinput/react-tagsinput.css'
import Dropzone from 'react-dropzone'
import Axios from 'axios'
import Cookies from 'js-cookie'

const CreateProduct = (props) => {
  const [product, setProduct] = useState({
    title: undefined,
    description: undefined,
    sku: undefined,
  })
  const [productVariantPrices, setProductVariantPrices] = useState([])

  const [productVariants, setProductVariant] = useState([
    {
      option: 'size',
      tags: [],
    },
  ])

  const handleProduct = (event) => {
    const { name, value } = event.target
    setProduct((preState) => ({ ...preState, [name]: value }))
  }

  const handleAddClick = () => {
    let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(
      (el) => new String(el.title).toLocaleLowerCase()
    )
    let selected_variants = productVariants.map((el) => el.option)
    let available_variants = all_variants.filter(
      (entry1) => !selected_variants.some((entry2) => entry1 === entry2)
    )
    setProductVariant([
      ...productVariants,
      {
        option: available_variants[0],
        tags: [],
      },
    ])
  }

  // handle input change on tag input
  const handleInputTagOnChange = (value, index) => {
    let product_variants = [...productVariants]
    product_variants[index].tags = value
    setProductVariant(product_variants)

    checkVariant()
  }

  // remove product variant
  const removeProductVariant = (index) => {
    setProductVariant((variants) => variants.filter((_, idx) => idx !== index))
  }

  // check the variant and render all the combination
  const checkVariant = () => {
    setProductVariantPrices([])

    getCombn(productVariants).forEach((item) => {
      setProductVariantPrices((productVariantPrice) => [
        ...productVariantPrice,
        {
          title: Object.entries(item)
            .map((it) => it[1])
            .join('/'),
          variants: item,
          price: 0,
          stock: 0,
        },
      ])
    })
  }

  useEffect(() => {
    checkVariant()
  }, [productVariants])

  // combination algorithm
  function getCombn(variants) {
    return variants.reduce(
      (result, currentVariant) => {
        const newCombinations = []

        result.forEach((combination) => {
          currentVariant.tags.forEach((tag) => {
            newCombinations.push({
              ...combination,
              [currentVariant.option]: tag,
            })
          })
        })

        return newCombinations
      },
      [{}]
    )
  }

  const productVariantPriceUpdate = (event, index) => {
    const { name, value } = event.target
    setProductVariantPrices((variants) =>
      variants.map((item, idx) => {
        if (idx === index) {
          return { ...item, [name]: value }
        } else return item
      })
    )
  }

  // Save product
  let saveProduct = (event) => {
    event.preventDefault()
    Axios.post(
      '/product/create-api/',
      { ...product, product_variant_prices: productVariantPrices },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
      }
    )
      .then(() => alert('Product created successfully'))
      .catch((error) =>
        alert(
          Object.entries(error.response.data)
            .map((item) => `${item[0]}: ${item[1][0]}`)
            .join('\n')
        )
      )
  }

  return (
    <div>
      <section>
        <div className='row'>
          <div className='col-md-6'>
            <div className='card shadow mb-4'>
              <div className='card-body'>
                <div className='form-group'>
                  <label htmlFor=''>Product Name</label>
                  <input
                    type='text'
                    placeholder='Product Name'
                    className='form-control'
                    name='title'
                    onChange={handleProduct}
                  />
                </div>
                <div className='form-group'>
                  <label htmlFor=''>Product SKU</label>
                  <input
                    type='text'
                    placeholder='Product Name'
                    className='form-control'
                    name='sku'
                    onChange={handleProduct}
                  />
                </div>
                <div className='form-group'>
                  <label htmlFor=''>Description</label>
                  <textarea
                    id=''
                    cols='30'
                    rows='4'
                    className='form-control'
                    name='description'
                    onChange={handleProduct}
                  ></textarea>
                </div>
              </div>
            </div>

            <div className='card shadow mb-4'>
              <div className='card-header py-3 d-flex flex-row align-items-center justify-content-between'>
                <h6 className='m-0 font-weight-bold text-primary'>Media</h6>
              </div>
              <div className='card-body border'>
                <Dropzone
                  onDrop={(acceptedFiles) => console.log(acceptedFiles)}
                >
                  {({ getRootProps, getInputProps }) => (
                    <section>
                      <div {...getRootProps()}>
                        <input {...getInputProps()} />
                        <p>
                          Drag 'n' drop some files here, or click to select
                          files
                        </p>
                      </div>
                    </section>
                  )}
                </Dropzone>
              </div>
            </div>
          </div>

          <div className='col-md-6'>
            <div className='card shadow mb-4'>
              <div className='card-header py-3 d-flex flex-row align-items-center justify-content-between'>
                <h6 className='m-0 font-weight-bold text-primary'>Variants</h6>
              </div>
              <div className='card-body'>
                {productVariants.map((element, index) => {
                  return (
                    <div className='row' key={index}>
                      <div className='col-md-4'>
                        <div className='form-group'>
                          <label htmlFor=''>Option</label>
                          <select
                            className='form-control'
                            defaultValue={element.option}
                            disabled
                          >
                            <option key={index} value={element.option}>
                              {element.option}
                            </option>
                          </select>
                        </div>
                      </div>

                      <div className='col-md-8'>
                        <div className='form-group'>
                          {productVariants.length > 1 ? (
                            <label
                              htmlFor=''
                              className='float-right text-primary'
                              style={{ marginTop: '-30px' }}
                              onClick={() => removeProductVariant(index)}
                            >
                              remove
                            </label>
                          ) : (
                            ''
                          )}

                          <section style={{ marginTop: '30px' }}>
                            <TagsInput
                              value={element.tags}
                              style='margin-top:30px'
                              onChange={(value) =>
                                handleInputTagOnChange(value, index)
                              }
                            />
                          </section>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className='card-footer'>
                {productVariants.length !== 3 ? (
                  <button className='btn btn-primary' onClick={handleAddClick}>
                    Add another option
                  </button>
                ) : (
                  ''
                )}
              </div>

              <div className='card-header text-uppercase'>Preview</div>
              <div className='card-body'>
                <div className='table-responsive'>
                  <table className='table'>
                    <thead>
                      <tr>
                        <td>Variant</td>
                        <td>Price</td>
                        <td>Stock</td>
                      </tr>
                    </thead>
                    <tbody>
                      {productVariantPrices.map(
                        (productVariantPrice, index) => {
                          return (
                            <tr key={index}>
                              <td>{productVariantPrice.title}</td>
                              <td>
                                <input
                                  className='form-control'
                                  type='text'
                                  name='price'
                                  value={productVariantPrice.price}
                                  onChange={(event) =>
                                    productVariantPriceUpdate(event, index)
                                  }
                                />
                              </td>
                              <td>
                                <input
                                  className='form-control'
                                  type='text'
                                  name='stock'
                                  value={productVariantPrice.stock}
                                  onChange={(event) =>
                                    productVariantPriceUpdate(event, index)
                                  }
                                />
                              </td>
                            </tr>
                          )
                        }
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <button
          type='button'
          onClick={saveProduct}
          className='btn btn-lg btn-primary'
        >
          Save!
        </button>
        <button type='button' className='btn btn-secondary btn-lg'>
          Cancel
        </button>
      </section>
    </div>
  )
}

export default CreateProduct
